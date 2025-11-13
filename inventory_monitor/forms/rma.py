from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.models import RMA, Asset
from inventory_monitor.models.rma import RMAStatusChoices


class RMAForm(NetBoxModelForm):
    rma_number = forms.CharField(
        required=False,
        empty_value=None,
        label=_("RMA Number"),
        help_text=_("RMA identifier provided by vendor"),
    )

    fieldsets = (
        FieldSet(
            "rma_number",
            "asset",
            "status",
            "original_serial",
            "replacement_serial",
            name="RMA Information",
        ),
        FieldSet("date_issued", "date_replaced", name="Dates"),
        FieldSet("issue_description", "vendor_response", name="Description"),
        FieldSet("tags", name="Tags"),
    )

    asset = DynamicModelChoiceField(queryset=Asset.objects.all(), selector=True, required=True)
    status = forms.ChoiceField(
        choices=RMAStatusChoices,
        help_text="Status will automatically update asset serial when set to 'Completed' with a replacement serial",
    )
    comments = CommentField()

    class Meta:
        model = RMA
        fields = (
            "rma_number",
            "asset",
            "original_serial",
            "replacement_serial",
            "status",
            "date_issued",
            "date_replaced",
            "issue_description",
            "vendor_response",
            "tags",
            "comments",
        )
        widgets = {
            "date_issued": DatePicker(),
            "date_replaced": DatePicker(),
            "issue_description": forms.Textarea(attrs={"rows": 3}),
            "vendor_response": forms.Textarea(attrs={"rows": 3}),
        }


class RMAFilterForm(NetBoxModelFilterSetForm):
    model = RMA
    fieldsets = (
        FieldSet("q", "filter_id", "tag", name="General"),
        FieldSet(
            "rma_number",
            "asset_id",
            "status",
            name="RMA Details",
        ),
        FieldSet(
            "date_issued",
            "date_replaced",
            name="Dates",
        ),
        FieldSet(
            "original_serial__ic",
            "replacement_serial__ic",
            "serial",
            name="Serial Numbers",
        ),
    )

    rma_number = forms.CharField(required=False)
    asset_id = DynamicModelChoiceField(queryset=Asset.objects.all(), required=False)
    original_serial__ic = forms.CharField(required=False, label="Original Serial (icontains)")
    replacement_serial__ic = forms.CharField(required=False, label="Replacement Serial (icontains)")
    serial = forms.CharField(
        required=False,
        label="Serial (Original or Replacement)",
        help_text="Search in both original and replacement serial numbers",
    )
    tag = TagFilterField(model)
    date_issued = forms.DateField(required=False, widget=DatePicker())
    date_replaced = forms.DateField(required=False, widget=DatePicker())


class RMABulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(choices=add_blank_choice(RMAStatusChoices), required=False)
    date_issued = forms.DateField(required=False, widget=DatePicker())
    date_replaced = forms.DateField(required=False, widget=DatePicker())
    issue_description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 3}), label="Issue Description"
    )
    vendor_response = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}), label="Vendor Response")
    comments = CommentField(required=False)

    model = RMA
    nullable_fields = ("date_issued", "date_replaced")


1
