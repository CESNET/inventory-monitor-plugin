import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filtersets import register_filterset

from inventory_monitor.models import RMA


@register_filterset
class RMAFilterSet(NetBoxModelFilterSet):
    q = django_filters.CharFilter(method="search")
    rma_number = django_filters.CharFilter()
    original_serial = django_filters.CharFilter()
    replacement_serial = django_filters.CharFilter()
    serial = django_filters.CharFilter(method="filter_serial", label="Serial (Original or Replacement)")
    status = django_filters.MultipleChoiceFilter(
        choices=RMA.status.field.choices,
    )

    class Meta:
        model = RMA
        fields = [
            "id",
            "rma_number",
            "asset_id",
            "original_serial",
            "replacement_serial",
            "serial",
            "status",
            "date_issued",
            "date_replaced",
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(rma_number__icontains=value)
            | Q(original_serial__icontains=value)
            | Q(replacement_serial__icontains=value)
            | Q(issue_description__icontains=value)
            | Q(vendor_response__icontains=value)
        )

    def filter_serial(self, queryset, name, value):
        """
        Filter by serial number in either original_serial or replacement_serial fields.

        Args:
            queryset: The queryset to filter
            name: The filter field name
            value: The serial number to search for

        Returns:
            Filtered queryset matching either original or replacement serial
        """
        if not value.strip():
            return queryset
        return queryset.filter(Q(original_serial__icontains=value) | Q(replacement_serial__icontains=value))
