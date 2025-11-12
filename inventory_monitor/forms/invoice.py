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
from inventory_monitor.models import Contract, Invoice


class InvoiceForm(NetBoxModelForm):
    comments = CommentField(label="Comments")
    contract = DynamicModelChoiceField(queryset=Contract.objects.all(), required=True, selector=True)
    currency = forms.ChoiceField(
        required=False,
        label=_("Currency"),
        help_text=_("Required if price is set"),
    )
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())

    fieldsets = (
        FieldSet("name", "name_internal", "project", "contract", "description", name=_("Invoice Details")),
        FieldSet(InlineFields("price", "currency", label=_("Price")), name=_("Financial")),
        FieldSet("invoicing_start", "invoicing_end", name=_("Dates")),
        FieldSet("tags", name=_("Additional Information")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices with blank option
        self.fields["currency"].choices = add_blank_choice(get_currency_choices())
        # Don't set default - let currency be blank until user adds a price

    class Meta:
        model = Invoice
        fields = (
            "name",
            "name_internal",
            "project",
            "contract",
            "price",
            "currency",
            "invoicing_start",
            "invoicing_end",
            "description",
            "comments",
            "tags",
        )


class InvoiceFilterForm(NetBoxModelFilterSetForm):
    model = Invoice

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("name", "name_internal", "project", "description", name=_("Common")),
        FieldSet("price", "price__gte", "price__lte", "price__isnull", "currency", name=_("Price")),
        FieldSet("contract_id", name=_("Linked")),
        FieldSet(
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
    name = forms.CharField(required=False)
    name_internal = forms.CharField(required=False)
    project = forms.CharField(required=False)
    description = forms.CharField(required=False)
    contract_id = DynamicModelMultipleChoiceField(queryset=Contract.objects.all(), required=False, label=_("Contract"))
    price = forms.DecimalField(required=False)
    price__gte = forms.DecimalField(required=False, label=("Price (min)"))
    price__lte = forms.DecimalField(required=False, label=("Price (max)"))
    price__isnull = forms.ChoiceField(
        required=False,
        label=("Has Price"),
        choices=(
            ("", "Any"),
            ("false", "Yes"),
            ("true", "No"),
        ),
    )
    currency = forms.MultipleChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config
        self.fields["currency"].choices = get_currency_choices()

    invoicing_start__gte = forms.DateField(required=False, label=("Invoicing Start: From"), widget=DatePicker())
    invoicing_start__lte = forms.DateField(required=False, label=("Invoicing Start: Till"), widget=DatePicker())
    invoicing_start = forms.DateField(required=False, label=("Invoicing Start"), widget=DatePicker())

    invoicing_end__gte = forms.DateField(required=False, label=("Invoicing End: From"), widget=DatePicker())
    invoicing_end__lte = forms.DateField(required=False, label=("Invoicing End: Till"), widget=DatePicker())
    invoicing_end = forms.DateField(required=False, label=("Invoicing End"), widget=DatePicker())


class InvoiceBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(max_length=100, required=False)
    name_internal = forms.CharField(max_length=100, required=False)
    project = forms.CharField(max_length=100, required=False)
    description = forms.CharField(required=False)
    contract = DynamicModelChoiceField(queryset=Contract.objects.all(), required=False)
    price = forms.DecimalField(required=False)
    currency = forms.ChoiceField(choices=[], required=False)
    invoicing_start = forms.DateField(required=False, widget=DatePicker())
    invoicing_end = forms.DateField(required=False, widget=DatePicker())

    model = Invoice
    nullable_fields = ("name_internal", "project", "description", "price", "currency", "invoicing_start", "invoicing_end")

    fieldsets = (
        FieldSet("name", "name_internal", "project", "description", "contract", name=_("Common")),
        FieldSet("price", "currency", name=_("Financial")),
        FieldSet("invoicing_start", "invoicing_end", name=_("Dates")),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add blank choice for currency in bulk edit
        self.fields["currency"].choices = add_blank_choice(get_currency_choices())
