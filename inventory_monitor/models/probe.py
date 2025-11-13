from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from netbox.models.features import (
    CustomFieldsMixin,
    CustomLinksMixin,
    CustomValidationMixin,
    EventRulesMixin,
    ExportTemplatesMixin,
    JournalingMixin,
    TagsMixin,
)
from utilities.querysets import RestrictedQuerySet

from inventory_monitor.settings import get_probe_recent_days


class Probe(
    CustomFieldsMixin,
    CustomLinksMixin,
    CustomValidationMixin,
    ExportTemplatesMixin,
    JournalingMixin,
    TagsMixin,
    EventRulesMixin,
    models.Model,
):
    objects = RestrictedQuerySet.as_manager()
    time = models.DateTimeField()
    creation_time = models.DateTimeField(default=timezone.now, blank=True, null=True)
    device_descriptor = models.CharField(max_length=100, blank=True, null=True)
    site_descriptor = models.CharField(max_length=100, blank=True, null=True)
    location_descriptor = models.CharField(max_length=100, blank=True, null=True)
    part = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    serial = models.CharField(max_length=255)
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        to="dcim.Location",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    discovered_data = models.JSONField(default=dict, blank=True)
    category = models.CharField(blank=True, null=True, max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["serial"], name="invmon_probe_serial_idx"),
            models.Index(fields=["time"], name="invmon_probe_time_idx"),
            models.Index(fields=["serial", "time"], name="invmon_probe_serial_time_idx"),
        ]
        ordering = (
            "name",
            "serial",
            "time",
            "part",
            "description",
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            "category",
            "discovered_data",
        )

    def __str__(self):
        return f"{self.serial} - {self.name}" if self.name else f"{self.serial}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:probe", args=[self.pk])

    def clean(self):
        """
        Custom validation for Probe model.

        Validates:
        - Creation time is not after probe time
        """
        super().clean()

        # Validate relationship between creation_time and time
        if self.time and self.creation_time:
            # Ensure creation_time is not after time
            if self.creation_time > self.time:
                raise ValidationError({"creation_time": "Creation time cannot be after probe time."})

    def is_recently_probed(self, days=None):
        """
        Check if this probe was seen within the specified number of days.

        Args:
            days (int): Number of days to check (default: from plugin settings)

        Returns:
            bool: True if probed within the specified period, False otherwise
        """
        if days is None:
            days = get_probe_recent_days()

        if not self.time:
            return False
        return (timezone.now() - self.time).days <= days
