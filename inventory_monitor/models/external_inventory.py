from django.db import models
from django.db.models.deletion import ProtectedError
from django.urls import reverse
from django.utils.translation import gettext as _
from netbox.models import NetBoxModel
from taggit.managers import TaggableManager

from inventory_monitor.models.asset import Asset
from inventory_monitor.settings import get_external_inventory_status_config_safe


class ExternalInventory(NetBoxModel):
    """
    Model representing inventory items imported from external inventory management system

    Contains data directly mapped from the external system's export structure.
    """

    external_id = models.CharField(
        unique=True,
        verbose_name="External System ID",
        help_text="Unique identifier from external inventory system",
        # TODO: after Migration and setting up the external_id, make this field non nullable and blankable
        null=True,
        blank=True,
        max_length=64,
    )

    inventory_number = models.CharField(
        max_length=64,
        verbose_name="Inventory Number",
        help_text="Asset number from external inventory system",
    )
    name = models.CharField(max_length=255, verbose_name="Name", help_text="Item name or description")
    serial_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Serial Number",
        help_text="Serial or production number",
    )
    person_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Person ID",
        help_text="ID of the person responsible for this item",
    )
    person_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Person Name",
        help_text="Name of the person responsible for this item",
    )
    location_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Location Code",
        help_text="Code representing the location of this item",
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Location",
        help_text="Description of item location",
    )
    department_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Department Code",
        help_text="Department code",
    )
    project_code = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="Project Code",
        help_text="Project code",
    )
    user_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="User Name",
        help_text="Name of the user",
    )
    user_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Notes",
        help_text="Notes from the user",
    )
    split_asset = models.CharField(
        # max_length=1,
        blank=True,
        null=True,
        verbose_name="Split Asset",
        help_text="Whether this is a split/shared asset",
    )
    status = models.CharField(
        # max_length=1,
        blank=True,
        null=True,
        verbose_name="Status",
        help_text="Current status of the item",
    )

    ############## EXTRA FIELDS
    assets = models.ManyToManyField(
        to=Asset,
        related_name="external_inventory_items",
        blank=True,
        verbose_name="Assets",
        help_text="Associated internal asset records",
    )

    # Override tags field to avoid reverse accessor clash with other plugins
    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="inventory_monitor_external_inventories",
        blank=True,
    )

    class Meta:
        ordering = ("inventory_number", "name")
        verbose_name = "External Inventory Item"
        verbose_name_plural = "External Inventory Items"
        indexes = [
            models.Index(fields=["inventory_number"], name="ext_inv_invnum_idx"),
            models.Index(fields=["serial_number"], name="ext_inv_serial_idx"),
            models.Index(fields=["person_id"], name="ext_inv_personid_idx"),
            models.Index(fields=["location_code"], name="ext_inv_loccode_idx"),
            models.Index(fields=["department_code"], name="ext_inv_deptcode_idx"),
            models.Index(fields=["project_code"], name="ext_inv_projcode_idx"),
            models.Index(fields=["status"], name="ext_inv_status_idx"),
        ]
        # unique_together = [["inventory_number"]]

    def __str__(self):
        parts = [self.inventory_number, self.name]

        # Add serial if available
        if self.serial_number:
            parts.append(f"[SN: {self.serial_number}]")

        # Add person responsible
        if self.person_name:
            parts.append(f"→ {self.person_name}")

        return " ".join(parts)

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:externalinventory", args=[self.pk])

    def get_status_color(self):
        """Get the Bootstrap color class for the current status from configuration"""
        status_config, is_configured = get_external_inventory_status_config_safe()

        if not is_configured:
            return "secondary"

        # Get color for current status, default to 'secondary' if not found
        status_info = status_config.get(str(self.status), {})
        return status_info.get("color", "secondary")

    def get_status_display(self):
        """Get the human-readable status label from configuration"""

        status_config, is_configured = get_external_inventory_status_config_safe()

        if not is_configured:
            return str(self.status)

        # Get label for current status, default to the status value if not found
        status_info = status_config.get(str(self.status), {})
        return status_info.get("label", str(self.status))

    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion of external inventory items with associated assets.
        Raises a ProtectedError if the external inventory item has associated assets.
        """
        if self.assets.exists():
            raise ProtectedError(
                msg=_(
                    "Cannot delete an External Inventory item that is linked to Assets. "
                    "Please remove the asset associations first."
                ),
                protected_objects=list(self.assets.all()),
            )

        super().delete(*args, **kwargs)
