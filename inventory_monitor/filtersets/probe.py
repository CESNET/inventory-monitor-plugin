import django_filters
from dcim.models import Device
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import BaseFilterSet

from inventory_monitor.models import Probe


class ProbeFilterSet(BaseFilterSet):
    """
    Filter set for the Probe model.

    This filter set provides filtering options for the Probe model based on various fields such as device, site, location, part, name, serial, description, and category.

    Attributes:
        q (django_filters.CharFilter): A filter for searching based on multiple fields.
        tag (TagFilter): A filter for filtering based on tags.
        serial (django_filters.CharFilter): A filter for filtering based on the serial number.
        time__gte (django_filters.DateTimeFilter): A filter for filtering based on the time greater than or equal to a specified value.
        time__lte (django_filters.DateTimeFilter): A filter for filtering based on the time less than or equal to a specified value.
        latest_only_per_device (django_filters.BooleanFilter): A filter for filtering only the latest inventory per device.
        latest_only (django_filters.BooleanFilter): A filter for filtering only the latest inventory.
        device_id (django_filters.ModelMultipleChoiceFilter): A filter for filtering based on the device ID.
        device (django_filters.ModelMultipleChoiceFilter): A filter for filtering based on the device name.

    Methods:
        search(queryset, name, value): A method for performing a search based on the provided value.
        _latest_only_per_device(queryset, name, value): A method for filtering only the latest inventory per device.
        _latest_only(queryset, name, value): A method for filtering only the latest inventory.

    """

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()

    serial = django_filters.CharFilter(lookup_expr="icontains")
    time__gte = django_filters.DateTimeFilter(field_name="time", lookup_expr="gte")
    time__lte = django_filters.DateTimeFilter(field_name="time", lookup_expr="lte")
    latest_only_per_device = django_filters.BooleanFilter(
        method="_latest_only_per_device", label="Latest inventory (per device)"
    )

    latest_only = django_filters.BooleanFilter(method="_latest_only", label="Latest inventory")

    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device__id",
        queryset=Device.objects.all(),
        to_field_name="id",
        label="Device (ID)",
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name="device__name",
        queryset=Device.objects.all(),
        to_field_name="name",
        label="Device (name)",
    )

    class Meta:
        model = Probe
        fields = (
            "id",
            "device_descriptor",
            "site_descriptor",
            "location_descriptor",
            "part",
            "name",
            "serial",
            "device",
            "site",
            "location",
            "description",
            "category",
        )

    @property
    def qs(self):
        """
        Optimize queryset with select_related and prefetch_related
        to reduce N+1 query problems.
        """
        qs = super().qs
        return qs.select_related(
            'device',
            'site',
            'location'
        ).prefetch_related('tags')

    def search(self, queryset, name, value):
        """
        Perform a search based on the provided value.

        Args:
            queryset (QuerySet): The initial queryset to perform the search on.
            name (str): The name of the filter field.
            value (str): The search value.

        Returns:
            QuerySet: The filtered queryset based on the search value.

        """
        device_descriptor = Q(device_descriptor__icontains=value)
        site_descriptor = Q(site_descriptor__icontains=value)
        location_descriptor = Q(location_descriptor__icontains=value)
        part = Q(part__icontains=value)
        name = Q(name__icontains=value)
        serial = Q(serial__icontains=value)
        description = Q(description__icontains=value)
        return queryset.filter(
            device_descriptor | part | name | serial | description | site_descriptor | location_descriptor
        )

    def _latest_only_per_device(self, queryset, name, value):
        """
        Filter only the latest inventory per device.

        Args:
            queryset (QuerySet): The initial queryset to filter.
            name (str): The name of the filter field.
            value (bool): The filter value.

        Returns:
            QuerySet: The filtered queryset with only the latest inventory per device.

        """
        if value:
            latest_inventory_pks = (
                Probe.objects.all()
                .order_by("serial", "device_id", "-time")
                .distinct("serial", "device_id")
                .values("pk")
            )
            return queryset.filter(pk__in=latest_inventory_pks)
        else:
            return queryset

    def _latest_only(self, queryset, name, value):
        """
        Filter only the latest inventory.

        Args:
            queryset (QuerySet): The initial queryset to filter.
            name (str): The name of the filter field.
            value (bool): The filter value.

        Returns:
            QuerySet: The filtered queryset with only the latest inventory.

        """
        if value:
            latest_inventory_pks = Probe.objects.all().distinct("serial").order_by("serial", "-time").values("pk")
            return queryset.filter(pk__in=latest_inventory_pks)
        else:
            return queryset
