from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from taggit.managers import TaggableManager
from utilities.querysets import RestrictedQuerySet

from inventory_monitor.models.mixins import DateStatusMixin


class AssetService(NetBoxModel, DateStatusMixin):
    objects = RestrictedQuerySet.as_manager()
    service_start = models.DateField(
        blank=True,
        null=True,
    )
    service_end = models.DateField(
        blank=True,
        null=True,
    )
    service_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    service_currency = models.CharField(
        blank=True,
        null=True,
        help_text="Currency for the service price (required if service_price is set, including 0)",
    )
    service_category = models.CharField(max_length=255, blank=True, null=True)
    service_category_vendor = models.CharField(max_length=255, blank=True, null=True)
    asset = models.ForeignKey(
        to="inventory_monitor.asset",
        on_delete=models.PROTECT,
        related_name="services",
        blank=True,
        null=True,
    )
    contract = models.ForeignKey(
        to="inventory_monitor.contract",
        on_delete=models.PROTECT,
        related_name="services",
        blank=True,
        null=True,
    )
    description = models.CharField(max_length=255, blank=True, default="")
    comments = models.TextField(blank=True)

    # Override tags field to avoid reverse accessor clash with other plugins
    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="inventory_monitor_asset_services",
        blank=True,
    )

    class Meta:
        ordering = (
            "service_start",
            "service_end",
            "service_price",
            "service_currency",
            "service_category",
            "service_category_vendor",
            "asset",
            "contract",
        )

    @property
    def asset_display(self):
        """
        Safe asset display for composite use.
        Returns asset string representation without PK, or fallback if None.
        """
        if not self.asset:
            return "No Asset"
        return self.asset.str_no_pk()

    def __str__(self):
        parts = []

        if self.asset:
            parts.append(self.asset.str_no_pk())  # Uses helper without PK

        if self.contract:
            parts.append(f"({self.contract.name})")

        if self.service_category:
            parts.append(f"[{self.service_category}]")

        if parts:
            return " ".join(parts)
        return f"#{self.pk}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:assetservice", args=[self.pk])

    def clean(self):
        super().clean()

        # Validate - currency is required if price is set (including 0)
        if self.service_price is not None and not self.service_currency:
            raise ValidationError({"service_currency": "Currency is required when service price is set."})

        # If currency is set, price must also be set
        if self.service_currency and self.service_price is None:
            raise ValidationError({"service_price": "Service price is required when currency is set."})

    def get_service_status(self):
        """Returns the service status and color for progress bar"""
        return self.get_date_status("service_start", "service_end", "Service")
