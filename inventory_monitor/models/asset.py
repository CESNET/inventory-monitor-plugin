from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Case, OuterRef, ProtectedError, Q, Subquery, Value, When
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from netbox.models import ImageAttachmentsMixin, NetBoxModel
from taggit.managers import TaggableManager
from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet

from inventory_monitor.models.mixins import DateStatusMixin
from inventory_monitor.models.probe import Probe
from inventory_monitor.settings import get_probe_recent_days

ASSIGNED_OBJECT_MODELS_QUERY = Q(
    app_label="dcim",
    model__in=(
        "site",
        "location",
        "rack",
        "device",
        "module",
    ),
)


class AssignmentStatusChoices(ChoiceSet):
    key = "inventory_monitor.asset.assignment_status"

    RESERVED = "reserved"
    DEPLOYED = "deployed"
    LOANED = "loaned"
    STOCKED = "stocked"

    CHOICES = [
        (RESERVED, "Reserved", "cyan"),
        (DEPLOYED, "Deployed", "green"),
        (LOANED, "Loaned", "blue"),
        (STOCKED, "Stocked", "gray"),
    ]


class LifecycleStatusChoices(ChoiceSet):
    key = "inventory_monitor.asset.lifecycle_status"

    NEW = "new"
    IN_STOCK = "in_stock"
    IN_USE = "in_use"
    IN_MAINTENANCE = "in_maintenance"
    RETIRED = "retired"
    DISPOSED = "disposed"

    CHOICES = [
        (NEW, "New", "green"),
        (IN_STOCK, "In Stock", "blue"),
        (IN_USE, "In Use", "cyan"),
        (IN_MAINTENANCE, "In Maintenance", "orange"),
        (RETIRED, "Retired", "red"),
        (DISPOSED, "Disposed", "gray"),
    ]


class Asset(NetBoxModel, DateStatusMixin, ImageAttachmentsMixin):
    objects = RestrictedQuerySet.as_manager()

    #
    # Basic identification fields
    #
    partnumber = models.CharField(max_length=64, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, default="")
    serial = models.CharField(max_length=255, blank=False, null=False)
    #
    # Status fields
    #
    assignment_status = models.CharField(
        max_length=30,
        choices=AssignmentStatusChoices,
        default=AssignmentStatusChoices.STOCKED,
        blank=False,
        null=False,
    )
    lifecycle_status = models.CharField(
        max_length=30,
        choices=LifecycleStatusChoices,
        default=LifecycleStatusChoices.NEW,
        blank=False,
        null=False,
    )

    #
    # Assignment fields using GenericForeignKey
    #
    assigned_object_type = models.ForeignKey(
        to="contenttypes.ContentType",
        limit_choices_to=ASSIGNED_OBJECT_MODELS_QUERY,
        on_delete=models.PROTECT,
        related_name="+",
        blank=True,
        null=True,
    )
    assigned_object_id = models.PositiveBigIntegerField(blank=True, null=True)
    assigned_object = GenericForeignKey(ct_field="assigned_object_type", fk_field="assigned_object_id")

    #
    # Related objects
    #
    type = models.ForeignKey(
        to="inventory_monitor.AssetType",
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )
    order_contract = models.ForeignKey(
        to="inventory_monitor.contract",
        on_delete=models.PROTECT,
        related_name="assets",
        blank=True,
        null=True,
    )

    #
    # Additional information
    #
    project = models.CharField(max_length=32, blank=True, null=True)
    vendor = models.CharField(max_length=32, blank=True, null=True)
    quantity = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=1,
        validators=[MinValueValidator(0)],
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        blank=True,
        null=True,
        help_text="Currency code (e.g., USD, EUR, CZK). Required if price is set, including 0.",
    )

    #
    # Warranty information
    #
    warranty_start = models.DateField(
        blank=True,
        null=True,
    )
    warranty_end = models.DateField(
        blank=True,
        null=True,
    )

    #
    # Notes
    #
    comments = models.TextField(blank=True)

    # Override tags field to avoid reverse accessor clash with other plugins
    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="inventory_monitor_assets",
        blank=True,
    )

    class Meta:
        db_table = "inventory_monitor_asset"
        ordering = (
            "partnumber",
            "serial",
            "description",
            "project",
            "vendor",
            "quantity",
            "price",
            "currency",
            "order_contract",
            "warranty_start",
            "warranty_end",
        )
        indexes = [
            models.Index(fields=["description"], name="invmon_asset_desc_idx"),
            models.Index(fields=["serial"], name="invmon_asset_serial_idx"),
            models.Index(fields=["partnumber"], name="invmon_asset_partnumber_idx"),
            models.Index(fields=["assignment_status"], name="invmon_asset_assign_status_idx"),
            models.Index(fields=["lifecycle_status"], name="invmon_asset_lifecycle_idx"),
            models.Index(fields=["vendor"], name="invmon_asset_vendor_idx"),
            models.Index(fields=["project"], name="invmon_asset_project_idx"),
            models.Index(fields=["warranty_start"], name="invmon_asset_warr_start_idx"),
            models.Index(fields=["warranty_end"], name="invmon_asset_warr_end_idx"),
            models.Index(
                fields=["assigned_object_type", "assigned_object_id"],
                name="invmon_asset_assigned_obj_idx",
            ),
        ]

    def get_related_probes(self):
        """
        Get all probe records related to this asset through various serial number matches:
        - serial (Current serial)
        - RMA serial numbers (from related RMAs)

        Returns:
        - QuerySet of Probe objects ordered by time descending
        """

        serials = {self.serial}
        rma_original_serials = set(self.rmas.values_list("original_serial", flat=True))
        rma_replacement_serials = set(self.rmas.values_list("replacement_serial", flat=True))

        # add rma_original_serials and rma_replacement_serials to serials
        serials.update(rma_original_serials)
        serials.update(rma_replacement_serials)
        # get rid of None values
        serials = [s for s in serials if s]

        return Probe.objects.filter(serial__in=serials).order_by("-time")

    def get_last_probe_time(self):
        """
        Get the timestamp of the most recent probe for this asset.

        Uses annotated value if available (set by annotate_with_probe_data).
        Falls back to querying if not annotated.

        Returns:
        - datetime: The time of the most recent probe, or None if no probes exist
        """
        # Check if this was queried with annotation
        if hasattr(self, "annotated_last_probe_time"):
            return self.annotated_last_probe_time

        # Fall back to querying if no annotation exists
        latest_probe = self.get_related_probes().first()
        return latest_probe.time if latest_probe else None

    def is_recently_probed(self, days=None):
        """
        Check if this asset has been probed within the specified number of days.

        Uses annotated value if available (set by annotate_with_probe_data).
        Falls back to querying if not annotated.

        Args:
            days (int): Number of days to check (default: from plugin settings)

        Returns:
            bool: True if probed within the specified period, False otherwise
        """
        # Check if this was queried with annotation
        if hasattr(self, "annotated_is_recently_probed"):
            return self.annotated_is_recently_probed

        if days is None:
            days = get_probe_recent_days()

        last_probe = self.get_last_probe_time()
        if not last_probe:
            return False
        return (timezone.now() - last_probe).days <= days

    def get_probe_recent_days_setting(self):
        """Get the probe recent days setting for template use."""
        return get_probe_recent_days()

    @classmethod
    def annotate_with_probe_data(cls, queryset):
        """
        Annotate queryset with last_probe_time and is_recently_probed values using raw SQL.

        This avoids the N+1 problem by using a simple JOIN to RMA and getting the latest probe
        for each serial in a single efficient query.

        The annotated fields can be accessed as:
        - annotated_last_probe_time: datetime of last probe
        - annotated_is_recently_probed: boolean indicating if probed recently

        Usage in views:
            queryset = Asset.objects.all()
            queryset = Asset.annotate_with_probe_data(queryset)

        Args:
            queryset: QuerySet of Asset objects

        Returns:
            QuerySet: Annotated queryset with probe data
        """

        # Get the probe recent days setting
        probe_recent_days = get_probe_recent_days()
        cutoff_date = timezone.now() - timedelta(days=probe_recent_days)

        # Simple efficient subquery: get the max probe time for each asset's own serial
        # This is much faster than trying to include RMA serials in the subquery
        latest_probe_subquery = Subquery(
            Probe.objects.filter(serial=OuterRef("serial")).order_by("-time").values("time")[:1]
        )

        # Annotate with last probe time
        queryset = queryset.annotate(annotated_last_probe_time=latest_probe_subquery)

        # Annotate with is_recently_probed boolean
        queryset = queryset.annotate(
            annotated_is_recently_probed=Case(
                When(
                    annotated_last_probe_time__isnull=False,
                    annotated_last_probe_time__gte=cutoff_date,
                    then=Value(True),
                ),
                default=Value(False),
                output_field=models.BooleanField(),
            )
        )

        return queryset

    def get_external_inventory_asset_numbers(self):
        """Get all External Inventory numbers associated with this asset"""
        return (
            self.external_inventory_items.filter(inventory_number__isnull=False)
            .exclude(inventory_number="")
            .values_list("inventory_number", flat=True)
            .distinct()
            .order_by("inventory_number")
        )

    def get_external_inventory_asset_numbers_display(self):
        """Get formatted display of External Inventory asset numbers"""
        numbers = list(self.get_external_inventory_asset_numbers())
        if not numbers:
            return None
        elif len(numbers) == 1:
            return numbers[0]
        else:
            return ", ".join(numbers)

    def get_external_inventory_asset_numbers_for_search(self):
        return " ".join(self.get_external_inventory_asset_numbers())

    def __str__(self):
        parts = []
        if self.partnumber:
            parts.append(self.partnumber)
        if self.serial:
            parts.append(f"[{self.serial}]")
        if self.vendor:
            parts.append(f"({self.vendor})")

        return " ".join(parts) if parts else f"#{self.pk}"

    def str_no_pk(self):
        if self.partnumber:
            return f"{self.partnumber} ({self.serial})"
        return f"{self.serial}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:asset", args=[self.pk])

    def clean(self):
        super().clean()

        # Validate price and currency relationship
        if self.price is not None:
            if not self.currency:
                raise ValidationError({"currency": _("Currency is required when price is set.")})

        # If currency is set, price must also be set
        if self.currency and self.price is None:
            raise ValidationError({"price": _("Price is required when currency is set.")})

    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion of assets with associated contracts.
        Raises a ProtectedError if the asset has an order_contract.
        """
        if self.order_contract:
            raise ProtectedError(
                msg=_(
                    "Cannot delete an Asset that is linked to a Contract. "
                    "Please remove the order_contract association first."
                ),
                protected_objects=[self.order_contract],
            )

        if items := self.external_inventory_items.all():
            raise ProtectedError(
                msg=_(
                    "Cannot delete an Asset that is linked to a External Inventory Items. "
                    "Please remove the external inventory items association first."
                ),
                protected_objects=list(items),
            )

        super().delete(*args, **kwargs)

    def get_assignment_status_color(self):
        return AssignmentStatusChoices.colors.get(self.assignment_status, "gray")

    def get_lifecycle_status_color(self):
        return LifecycleStatusChoices.colors.get(self.lifecycle_status, "gray")

    def get_warranty_status(self):
        """Returns the warranty status and color for progress bar"""
        return self.get_date_status("warranty_start", "warranty_end", "Warranty")
