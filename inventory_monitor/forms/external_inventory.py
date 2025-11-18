from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from inventory_monitor.models import Asset, ExternalInventory
from inventory_monitor.settings import get_external_inventory_status_config_safe


class ExternalInventoryForm(NetBoxModelForm):
    """
    Form for creating and editing External Inventory objects
    """

    comments = CommentField(label="Comments")
    assets = DynamicModelMultipleChoiceField(
        queryset=Asset.objects.all(),
        required=False,
        label="Associated Assets",
        selector=True,
    )
    split_asset = forms.CharField(
        required=False,
        label="Split Asset",
        help_text="Whether this is a split/shared asset",
    )
    status = forms.CharField(
        required=False,
        label="Status",
        help_text="",  # Will be set in __init__
    )

    fieldsets = (
        FieldSet(
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            name=_("Asset Identification"),
        ),
        FieldSet(
            "person_id",
            "person_name",
            name=_("Person Information"),
        ),
        FieldSet(
            "location_code",
            "location",
            name=_("Location Information"),
        ),
        FieldSet(
            "department_code",
            "project_code",
            "user_name",
            "user_note",
            name=_("Usage Information"),
        ),
        FieldSet(
            "split_asset",
            "status",
            "assets",
            name=_("Status"),
        ),
        FieldSet("tags", name=_("Tags")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build dynamic help text for status field based on configuration
        status_config, is_configured = get_external_inventory_status_config_safe()

        if is_configured:
            status_help_parts = ["Available status codes:"]
            for code, info in sorted(status_config.items()):
                label = info.get("label", code)
                status_help_parts.append(f"{code} = {label}")
            self.fields["status"].help_text = " | ".join(status_help_parts)
        else:
            self.fields["status"].help_text = "Current status of the item"

    class Meta:
        model = ExternalInventory
        fields = (
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            "person_id",
            "person_name",
            "location_code",
            "location",
            "department_code",
            "project_code",
            "user_name",
            "user_note",
            "split_asset",
            "status",
            "assets",
            "tags",
            "comments",
        )


class ExternalInventoryBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(required=False, label="Name")
    person_name = forms.CharField(required=False, label="Person Name")
    location = forms.CharField(required=False, label="Location")
    status = forms.CharField(required=False, label="Status")
    comments = CommentField(required=False)

    model = ExternalInventory
    nullable_fields = ("name", "person_name", "location", "status", "comments")


class ExternalInventoryFilterForm(NetBoxModelFilterSetForm):
    """
    Filter form for External Inventory objects
    """

    model = ExternalInventory

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet(
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            name=_("Asset Identification"),
        ),
        FieldSet(
            "person_id",
            "person_name",
            name=_("Person Information"),
        ),
        FieldSet(
            "location_code",
            "location",
            name=_("Location Information"),
        ),
        FieldSet(
            "department_code",
            "project_code",
            "user_name",
            name=_("Usage Information"),
        ),
        FieldSet(
            "split_asset",
            "status",
            "asset_id",
            "has_assets",
            name=_("Status"),
        ),
    )

    tag = TagFilterField(model)
    external_id = forms.CharField(required=False)
    inventory_number = forms.CharField(required=False)
    name = forms.CharField(required=False)
    serial_number = forms.CharField(required=False)
    person_id = forms.CharField(required=False)
    person_name = forms.CharField(required=False)
    location_code = forms.CharField(required=False)
    location = forms.CharField(required=False)
    department_code = forms.CharField(required=False)
    project_code = forms.CharField(required=False)
    user_name = forms.CharField(required=False)
    split_asset = forms.CharField(required=False)
    status = forms.CharField(required=False)
    asset_id = DynamicModelMultipleChoiceField(queryset=Asset.objects.all(), required=False, label=_("Assets"))
    has_assets = forms.ChoiceField(
        choices=[
            ("", "All"),
            ("true", "With Assets"),
            ("false", "Without Assets"),
        ],
        required=False,
        label=_("Has Assets"),
        help_text=_("Filter by whether External Inventory object has assigned assets"),
    )
