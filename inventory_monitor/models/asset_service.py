from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
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
        help_text="Currency for the service price (required if service_price is set)",
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
    comments = models.TextField(blank=True)

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

    def __str__(self):
        return f"{self.pk}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:assetservice", args=[self.pk])

    def clean(self):
        super().clean()

        # Validate - currency is required if price is set
        if self.service_price is not None and self.service_price != 0 and not self.service_currency:
            raise ValidationError({"service_currency": "Currency is required when service price is set."})
        
        # If currency is set, price must also be set
        if self.service_currency and self.service_price is None:
            raise ValidationError({"service_price": "Service price is required when currency is set."})

    def get_service_status(self):
        """Returns the service status and color for progress bar"""
        return self.get_date_status("service_start", "service_end", "Service")
