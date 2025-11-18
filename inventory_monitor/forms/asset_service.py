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
from inventory_monitor.models import Asset, AssetService, Contract


class AssetServiceForm(NetBoxModelForm):
    fieldsets = (
        FieldSet("contract", "asset", "description", name=_("Linked")),
        FieldSet("service_start", "service_end", name=_("Dates")),
        FieldSet(
            InlineFields("service_price", "service_currency", label=_("Service Price")),
            "service_category",
            "service_category_vendor",
            name=_("Service Params"),
        ),
        FieldSet("tags", name=_("Additional Information")),
    )

    comments = CommentField(label="Comments")
    description = forms.CharField(required=False, label="Description")
    service_start = forms.DateField(required=False, label=("Service Start"), widget=DatePicker())
    service_end = forms.DateField(required=False, label=("Service End"), widget=DatePicker())
    service_price = forms.DecimalField(
        required=False,
        label="Service Price",
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter price'}),
    )
    service_currency = forms.ChoiceField(
        required=False,
        label=_("Currency"),
        help_text=_("Required if service price is set"),
    )
    service_category = forms.CharField(
        required=False,
        label="Service Category",
    )
    service_category_vendor = forms.CharField(
        required=False,
        label="Service Category Vendor",
    )
    asset = DynamicModelChoiceField(
        queryset=Asset.objects.all(),
        required=True,
        label="Service Asset",
        selector=True
    )
    contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        required=True,
        label="Service Contract",
        selector=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices with blank option
        self.fields["service_currency"].choices = add_blank_choice(get_currency_choices())
        # Don't set default - let currency be blank until user adds a service price

    class Meta:
        model = AssetService
        fields = (
            "service_start",
            "service_end",
            "service_price",
            "service_currency",
            "service_category",
            "service_category_vendor",
            "asset",
            "contract",
            "description",
            "comments",
            "tags",
        )


class AssetServiceFilterForm(NetBoxModelFilterSetForm):
    model = AssetService

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("asset", "contract", "description", name=_("Linked")),
        FieldSet(
            "service_start",
            "service_start__gte",
            "service_start__lte",
            "service_end",
            "service_end__gte",
            "service_end__lte",
            name=_("Dates"),
        ),
        FieldSet(
            "service_price",
            "service_price__gte",
            "service_price__lte",
            "service_price__isnull",
            "service_currency",
            "service_category",
            "service_category_vendor",
            name=_("Service"),
        ),
    )

    tag = TagFilterField(model)
    service_start = forms.DateField(required=False, label=("Service Start"), widget=DatePicker())
    description = forms.CharField(required=False, label="Description")
    service_start__gte = forms.DateField(required=False, label=("Service Start: From"), widget=DatePicker())
    service_start__lte = forms.DateField(required=False, label=("Service Start: Till"), widget=DatePicker())
    service_end = forms.DateField(required=False, label=("Service End"), widget=DatePicker())
    service_end__gte = forms.DateField(required=False, label=("Service End: From"), widget=DatePicker())
    service_end__lte = forms.DateField(required=False, label=("Service End: Till"), widget=DatePicker())
    service_price = forms.DecimalField(
        required=False,
        label="Service Price",
        min_value=0,
        decimal_places=2,
    )
    service_price__gte = forms.DecimalField(
        required=False,
        label="Service Price (min)",
        min_value=0,
        decimal_places=2,
    )
    service_price__lte = forms.DecimalField(
        required=False,
        label="Service Price (max)",
        min_value=0,
        decimal_places=2,
    )
    service_price__isnull = forms.ChoiceField(
        required=False,
        label=("Has Service Price"),
        choices=(
            ('', 'Any'),
            ('false', 'Yes'),
            ('true', 'No'),
        ),
    )
    service_currency = forms.MultipleChoiceField(required=False)
    service_category = forms.CharField(
        required=False,
        label="Service Category",
    )
    service_category_vendor = forms.CharField(
        required=False,
        label="Service Category Vendor",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config
        self.fields["service_currency"].choices = get_currency_choices()

    asset = DynamicModelMultipleChoiceField(queryset=Asset.objects.all(), required=False, label=_("Asset"))
    contract = DynamicModelMultipleChoiceField(queryset=Contract.objects.all(), required=False, label=_("Contract"))


class AssetServiceBulkEditForm(NetBoxModelBulkEditForm):
    service_start = forms.DateField(required=False, label=("Service Start"), widget=DatePicker())
    service_end = forms.DateField(required=False, label=("Service End"), widget=DatePicker())
    service_price = forms.DecimalField(
        required=False,
        label="Service Price",
        min_value=0,
        decimal_places=2,
    )
    service_currency = forms.ChoiceField(required=False)
    description = forms.CharField(required=False, label="Description")
    service_category = forms.CharField(
        required=False,
        label="Service Category",
    )
    service_category_vendor = forms.CharField(
        required=False,
        label="Service Category Vendor",
    )
    asset = DynamicModelChoiceField(
        queryset=Asset.objects.all(),
        required=False,
        label="Service Asset",
    )
    contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(),
        required=False,
        label="Service Contract",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config with blank option
        self.fields["service_currency"].choices = add_blank_choice(get_currency_choices())

    model = AssetService
    fieldsets = (
        FieldSet("service_start", "service_end", name=_("Dates")),
        FieldSet(
            "service_price",
            "service_currency",
            "service_category",
            "service_category_vendor",
            "description",
            name=_("Service Params"),
        ),
        FieldSet("asset", "contract", name=_("Linked")),
    )
    nullable_fields = (
        "service_start",
        "service_end",
        "service_price",
        "service_currency",
        "service_category",
        "service_category_vendor",
        "description",
    )
