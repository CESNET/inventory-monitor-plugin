import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filtersets import register_filterset

from inventory_monitor.models import AssetType


@register_filterset
class AssetTypeFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = AssetType
        fields = ["id", "name", "slug", "description", "color"]

    name = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter(lookup_expr="icontains")
    slug = django_filters.CharFilter(lookup_expr="iexact")

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(Q(name__icontains=value) | Q(slug__icontains=value) | Q(description__icontains=value))
