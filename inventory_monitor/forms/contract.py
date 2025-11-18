from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets.datetime import DatePicker

from inventory_monitor.helpers import get_currency_choices
from inventory_monitor.models import Contract, Contractor, ContractTypeChoices


class ContractForm(NetBoxModelForm):
    comments = CommentField(label="Comments")
    contractor = DynamicModelChoiceField(queryset=Contractor.objects.all(), required=True, selector=True)
    parent = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        query_params={"parent_id": "null"},
        required=False,
        label=("Parent Contract"),
        selector=True,
    )
    currency = forms.ChoiceField(
        required=False,
        label=_("Currency"),
        help_text=_("Required if price is set"),
    )
    signed = forms.DateField(required=False, label=("Signed"), widget=DatePicker())
    accepted = forms.DateField(required=False, label=("Accepted"), widget=DatePicker())
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())

    fieldsets = (
        FieldSet("name", "name_internal", "contractor", "type", name=_("Contract Details")),
        FieldSet(InlineFields("price", "currency", label=_("Price")), name=_("Financial")),
        FieldSet(
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            name=_("Dates"),
        ),
        FieldSet("parent", name=_("Hierarchy")),
        FieldSet("tags", name=_("Additional Information")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices with blank option
        self.fields["currency"].choices = add_blank_choice(get_currency_choices())
        # Don't set default - let currency be blank until user adds a price

    class Meta:
        model = Contract
        fields = (
            "name",
            "name_internal",
            "contractor",
            "type",
            "price",
            "currency",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            "parent",
            "description",
            "comments",
            "tags",
        )


class ContractFilterForm(NetBoxModelFilterSetForm):
    model = Contract

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("name", "name_internal", "contract_type", "type", "description", name=_("Common")),
        FieldSet("price", "price__gte", "price__lte", "price__isnull", "currency", name=_("Price")),
        FieldSet("contractor_id", "parent_id", name=_("Linked")),
        FieldSet(
            "signed",
            "signed__gte",
            "signed__lte",
            "accepted",
            "accepted__gte",
            "accepted__lte",
            "invoicing_start",
            "invoicing_start__gte",
            "invoicing_start__lte",
            "invoicing_end",
            "invoicing_end__gte",
            "invoicing_end__lte",
            name=_("Dates"),
        ),
    )
    tag = TagFilterField(model)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config
        self.fields["currency"].choices = get_currency_choices()

    name = forms.CharField(required=False)
    name_internal = forms.CharField(required=False)
    description = forms.CharField(required=False)
    contract_type = forms.ChoiceField(
        label="Contract Type",
        choices=(
            ("All", "All"),
            ("Contract", "Contract"),
            ("Subcontract", "Subcontract"),
        ),
        required=False,
        initial="All",
    )
    contractor_id = DynamicModelMultipleChoiceField(
        queryset=Contractor.objects.all(), required=False, label=_("Contractor")
    )

    parent_id = DynamicModelMultipleChoiceField(
        queryset=Contract.objects.filter(parent_id=None),
        required=False,
        label=_("Parent Contract"),
    )
    type = forms.MultipleChoiceField(choices=ContractTypeChoices, required=False)
    price = forms.DecimalField(required=False)
    price__gte = forms.DecimalField(required=False, label=("Price (min)"))
    price__lte = forms.DecimalField(required=False, label=("Price (max)"))
    price__isnull = forms.ChoiceField(
        required=False,
        label=("Price is null"),
        choices=(
            ("", "Any"),
            ("true", "Yes"),
            ("false", "No"),
        ),
    )
    currency = forms.MultipleChoiceField(required=False)
    accepted__gte = forms.DateField(required=False, label=("Accepted From"), widget=DatePicker())
    accepted__lte = forms.DateField(required=False, label=("Accepted Till"), widget=DatePicker())
    accepted = forms.DateField(required=False, label=("Accepted"), widget=DatePicker())
    signed__gte = forms.DateField(required=False, label=("Signed From"), widget=DatePicker())
    signed__lte = forms.DateField(required=False, label=("Signed Till"), widget=DatePicker())
    signed = forms.DateField(required=False, label=("Signed"), widget=DatePicker())
    invoicing_start__gte = forms.DateField(required=False, label=("Invoicing Start: From"), widget=DatePicker())
    invoicing_start__lte = forms.DateField(required=False, label=("Invoicing Start: Till"), widget=DatePicker())
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())

    invoicing_end__gte = forms.DateField(required=False, label=("Invoicing End: From"), widget=DatePicker())
    invoicing_end__lte = forms.DateField(required=False, label=("Invoicing End: Till"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())


class ContractBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(max_length=100, required=False)
    name_internal = forms.CharField(max_length=100, required=False)
    description = forms.CharField(required=False)
    contractor = DynamicModelChoiceField(queryset=Contractor.objects.all(), required=False)
    type = forms.ChoiceField(required=False, choices=add_blank_choice(ContractTypeChoices))
    price = forms.DecimalField(required=False)
    currency = forms.ChoiceField(required=False)
    signed = forms.DateField(required=False, widget=DatePicker())
    accepted = forms.DateField(required=False, widget=DatePicker())
    invoicing_start = forms.DateField(required=False, widget=DatePicker())
    invoicing_end = forms.DateField(required=False, widget=DatePicker())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config with blank option
        self.fields["currency"].choices = add_blank_choice(get_currency_choices())

    model = Contract
    nullable_fields = (
        "name_internal",
        "description",
        "price",
        "currency",
        "signed",
        "accepted",
        "invoicing_start",
        "invoicing_end",
    )
