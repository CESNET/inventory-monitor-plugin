from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from inventory_monitor.models import Contractor

# Get max_length values from model
COMPANY_MAX = Contractor._meta.get_field("company").max_length
ADDRESS_MAX = Contractor._meta.get_field("address").max_length


class ContractorForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), selector=True, required=False)

    comments = CommentField(label="Comments")

    class Meta:
        model = Contractor
        fields = ("name", "company", "address", "description", "tenant", "tags", "comments")


class ContractorFilterForm(NetBoxModelFilterSetForm):
    model = Contractor
    tag = TagFilterField(model)
    name = forms.CharField(required=False)
    company = forms.CharField(required=False)
    address = forms.CharField(required=False)
    description = forms.CharField(required=False)
    tenant_id = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False, label="Tenant")

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("name", "company", "address", "description", name=_("Common")),
        FieldSet("tenant_id", name=_("Linked")),
    )


class ContractorBulkEditForm(NetBoxModelBulkEditForm):
    company = forms.CharField(max_length=COMPANY_MAX, required=False)
    address = forms.CharField(max_length=ADDRESS_MAX, required=False)
    description = forms.CharField(required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    model = Contractor
    nullable_fields = ("company", "address", "description", "tenant")


class ContractorBulkImportForm(NetBoxModelImportForm):
    """
    Form for bulk importing Contractors
    """

    name = forms.CharField(required=True, help_text="Contractor name (required)")
    company = forms.CharField(required=False, help_text="Company or organization name")
    address = forms.CharField(required=False, help_text="Contractor's address")
    description = forms.CharField(required=False, help_text="Short description of the contractor")
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Tenant name to associate with this contractor",
    )

    class Meta:
        model = Contractor
        fields = [
            "name",
            "company",
            "address",
            "description",
            "tenant",
            "tags",
        ]
