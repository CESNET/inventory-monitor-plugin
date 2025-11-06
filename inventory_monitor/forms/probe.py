import datetime

from dcim.models import Device, Location, Site
from django import forms
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import (
    CommentField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets.datetime import DatePicker, DateTimePicker

from inventory_monitor.models import Probe


class ProbeForm(NetBoxModelForm):
    comments = CommentField(label="Comments")
    site = DynamicModelChoiceField(queryset=Site.objects.all(), required=False)
    location = DynamicModelChoiceField(queryset=Location.objects.all(), required=False)

    class Meta:
        model = Probe
        fields = (
            "name",
            "serial",
            "time",
            "category",
            "part",
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            "description",
            "tags",
            "comments",
        )


class ProbeFilterForm(NetBoxModelFilterSetForm):
    model = Probe

    # TODO: Add FilterSets, Add FilterForm
    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        FieldSet("device_id", name=_("Linked")),
        FieldSet("time__gte", "time__lte", name=_("Dates")),
        FieldSet("serial", "category", "device_descriptor", "description", name=_("Common")),
        FieldSet("latest_only_per_device", "latest_only", name=_("Misc")),
    )

    tag = TagFilterField(model)
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label=_("Device"))
    serial = forms.CharField(required=False)
    device_descriptor = forms.CharField(required=False)
    category = forms.CharField(required=False)
    description = forms.CharField(required=False)
    time__gte = forms.DateTimeField(required=False, label=("Time From"), widget=DateTimePicker())
    time__lte = forms.DateTimeField(required=False, label=("Time Till"), widget=DateTimePicker())
    latest_only_per_device = forms.BooleanField(
        required=False,
        label="Latest inventory only (per device)",
        widget=forms.NullBooleanSelect()
    )
    latest_only = forms.BooleanField(
        required=False,
        label="Latest inventory only",
        widget=forms.NullBooleanSelect()
    )


class ProbeDiffForm(NetBoxModelForm):
    date_from = forms.DateField(
        required=True,
        label=("Date From"),
        widget=DatePicker(),
        initial=datetime.date.today() - datetime.timedelta(days=90),
    )
    date_to = forms.DateField(
        required=True,
        label=("Date To"),
        widget=DatePicker(),
        initial=datetime.date.today(),
    )
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=True, label=_("Device"))

    # Hidden field for tags
    tags = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Probe
        fields = ("date_from", "date_to", "device")
