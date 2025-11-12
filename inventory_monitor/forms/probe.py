import datetime

from dcim.models import Device, Location, Site
from django import forms
from django.utils import timezone
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
    """
    Form for creating and editing Probe objects
    """

    # Comments field
    comments = CommentField(label=_("Comments"))

    # Date/time field with proper widget
    time = forms.DateTimeField(
        required=True,
        label=_("Discovery Time"),
        help_text=_("When this hardware was discovered (cannot be after creation time)"),
        widget=DateTimePicker(),
    )

    # Creation time field with current time as default
    creation_time = forms.DateTimeField(
        required=False,
        label=_("Creation Time"),
        help_text=_("When this probe entry was created in the system (optional, defaults to current time if not set)"),
        widget=DateTimePicker(),
        initial=timezone.now,
    )

    # Part number field
    part = forms.CharField(
        required=False,
        label=_("Part Number"),
        help_text=_("Hardware part number or model identifier"),
    )

    # Linked objects
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Linked Device"),
        help_text=_("NetBox device where this hardware was discovered"),
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_("Linked Site"),
        help_text=_("NetBox site where this hardware was discovered"),
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_("Linked Location"),
        help_text=_("NetBox location where this hardware was discovered"),
    )

    fieldsets = (
        FieldSet("name", "serial", "category", "part", name=_("Hardware Identification")),
        FieldSet("time", "creation_time", name=_("Discovery Information")),
        FieldSet(
            "device_descriptor",
            "device",
            "site_descriptor",
            "site",
            "location_descriptor",
            "location",
            name=_("Linked Objects"),
        ),
        FieldSet("description", name=_("Description")),
        FieldSet("tags", name=_("Additional Information")),
    )

    class Meta:
        model = Probe
        fields = (
            "name",
            "serial",
            "time",
            "creation_time",
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
    """
    Filter form for Probe list view
    """

    model = Probe

    fieldsets = (
        FieldSet("q", "filter_id", "tag", name=_("Search & Tags")),
        FieldSet("device_id", name=_("Linked Objects")),
        FieldSet("time", "time__gte", "time__lte", name=_("Discovery Dates")),
        FieldSet("serial", "category", "device_descriptor", "description", name=_("Hardware Details")),
        FieldSet("latest_only_per_device", "latest_only", name=_("Display Options")),
    )

    # Search and filter
    tag = TagFilterField(model)

    # Linked objects
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_("Linked NetBox Device"),
        help_text=_("Filter by devices that have been linked to probe entries"),
    )

    # Hardware details
    serial = forms.CharField(
        required=False,
        label=_("Serial Number"),
        help_text=_("Filter by hardware serial number"),
    )
    device_descriptor = forms.CharField(
        required=False,
        label=_("Discovered Device Info"),
        help_text=_("Filter by raw device information from discovery"),
    )
    category = forms.CharField(
        required=False,
        label=_("Hardware Category"),
        help_text=_("Filter by hardware type/category"),
    )
    description = forms.CharField(
        required=False,
        label=_("Description"),
        help_text=_("Filter by description/notes"),
    )

    # Date/time filters with proper widgets
    time = forms.DateTimeField(
        required=False,
        label=_("Discovery Time"),
        help_text=_("Exact discovery date/time"),
        widget=DateTimePicker(),
    )
    time__gte = forms.DateTimeField(
        required=False,
        label=_("Discovery Time: From"),
        help_text=_("Show probes discovered after this date/time"),
        widget=DateTimePicker(),
    )
    time__lte = forms.DateTimeField(
        required=False,
        label=_("Discovery Time: To"),
        help_text=_("Show probes discovered before this date/time"),
        widget=DateTimePicker(),
    )

    # Display options
    latest_only_per_device = forms.NullBooleanField(
        required=False,
        label=_("Latest per device only"),
        help_text=_("Show only the most recent probe entry for each device"),
    )
    latest_only = forms.NullBooleanField(
        required=False,
        label=_("Latest entries only"),
        help_text=_("Show only the most recent probe entries overall"),
    )


class ProbeDiffForm(NetBoxModelForm):
    """
    Form for analyzing probe differences for a device over time
    """

    # Date range fields
    date_from = forms.DateField(
        required=True,
        label=_("Start Date"),
        help_text=_("Beginning of the date range to analyze"),
        widget=DatePicker(),
        initial=datetime.date.today() - datetime.timedelta(days=90),
    )
    date_to = forms.DateField(
        required=True,
        label=_("End Date"),
        help_text=_("End of the date range to analyze"),
        widget=DatePicker(),
        initial=datetime.date.today(),
    )

    # Target device
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=True,
        label=_("Target Device"),
        help_text=_("Select the device to analyze probe differences for"),
        selector=True
    )

    # Hidden field for tags
    tags = forms.CharField(widget=forms.HiddenInput())

    fieldsets = (
        FieldSet("date_from", "date_to", name=_("Date Range")),
        FieldSet("device", name=_("Target")),
    )

    class Meta:
        model = Probe
        fields = ("date_from", "date_to", "device")
