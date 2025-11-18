from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from taggit.managers import TaggableManager
from utilities.querysets import RestrictedQuerySet


class Invoice(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    name = models.CharField(max_length=255, blank=False, null=False)
    name_internal = models.CharField(max_length=255, blank=False, null=False)
    project = models.CharField(max_length=255, blank=True, null=True)
    contract = models.ForeignKey(
        to="inventory_monitor.contract",  # Contractor,
        on_delete=models.PROTECT,
        related_name="invoices",
        blank=False,
        null=False,
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
        help_text="Currency for the invoice price (required if price is set, including 0)",
    )
    invoicing_start = models.DateField(
        blank=True,
        null=True,
    )
    invoicing_end = models.DateField(
        blank=True,
        null=True,
    )
    description = models.CharField(max_length=255, blank=True, default="")
    comments = models.TextField(blank=True)

    # Override tags field to avoid reverse accessor clash with other plugins
    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="inventory_monitor_invoices",
        blank=True,
    )

    class Meta:
        ordering = (
            "name",
            "name_internal",
            "contract",
            "price",
            "currency",
            "invoicing_start",
            "invoicing_end",
        )

    def __str__(self):
        parts = [self.name]

        # Add contract context
        if self.contract:
            parts.append(f"({self.contract.name})")

        # Add project if useful
        if self.project and (not self.contract or self.project != self.contract.name):
            parts.append(f"[{self.project}]")

        # Add price if available
        if self.price is not None and self.currency:
            parts.append(f"{self.price} {self.currency}")

        return " ".join(parts)

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:invoice", args=[self.pk])

    def clean(self):
        super().clean()

        # Validate - currency is required if price is set (including 0)
        if self.price is not None and not self.currency:
            raise ValidationError({"currency": "Currency is required when price is set."})

        # If currency is set, price must also be set
        if self.currency and self.price is None:
            raise ValidationError({"price": "Price is required when currency is set."})

        # Validate invoicing_start and invoicing_end
        if self.invoicing_start and self.invoicing_end and self.invoicing_start > self.invoicing_end:
            raise ValidationError({"invoicing_start": "Invoicing Start cannot be set after Invoicing End"})
