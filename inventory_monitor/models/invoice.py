from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
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
        help_text="Currency for the invoice price (required if price is set)",
    )
    invoicing_start = models.DateField(
        blank=True,
        null=True,
    )
    invoicing_end = models.DateField(
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)

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
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:invoice", args=[self.pk])

    def clean(self):
        super().clean()

        # Validate - currency is required if price is set
        if self.price is not None and self.price != 0 and not self.currency:
            raise ValidationError({"currency": "Currency is required when price is set."})
        
        # If currency is set, price must also be set
        if self.currency and self.price is None:
            raise ValidationError({"price": "Price is required when currency is set."})

        # Validate invoicing_start and invoicing_end
        if self.invoicing_start and self.invoicing_end and self.invoicing_start > self.invoicing_end:
            raise ValidationError({"invoicing_start": "Invoicing Start cannot be set after Invoicing End"})
