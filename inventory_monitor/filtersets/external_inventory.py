import django_filters
from dcim.models import Location, Region, Site
from django.db.models import Q
from netbox.filtersets import PrimaryModelFilterSet
from tenancy.filtersets import ContactModelFilterSet
from utilities.filters import ContentTypeFilter, MultiValueCharFilter, MultiValueNumberFilter
from utilities.filtersets import register_filterset

from inventory_monitor.helpers import location_assignment_q
from inventory_monitor.models import Asset, ExternalInventory


@register_filterset
class ExternalInventoryFilterSet(PrimaryModelFilterSet, ContactModelFilterSet):
    """
    Filterset for External Inventory objects providing comprehensive search and filtering capabilities.
    """

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    external_id = django_filters.CharFilter()
    inventory_number = django_filters.CharFilter()
    name = django_filters.CharFilter()
    serial_number = django_filters.CharFilter()
    person_id = MultiValueCharFilter()
    person_name = MultiValueCharFilter()
    location_code = MultiValueCharFilter()
    location = MultiValueCharFilter()
    external_location_id = MultiValueCharFilter()
    department_code = MultiValueCharFilter()
    project_code = MultiValueCharFilter()
    user_name = MultiValueCharFilter()
    user_note = django_filters.CharFilter()
    split_asset = django_filters.CharFilter()
    status = MultiValueCharFilter()
    asset_id = django_filters.ModelMultipleChoiceFilter(
        field_name="assets",
        queryset=Asset.objects.all(),
        to_field_name="id",
        label="Asset (ID)",
        distinct=True,
    )

    # Nový filtr pro objekty s/bez přiřazených assetů
    has_assets = django_filters.BooleanFilter(
        method="filter_has_assets",
        label="Has Assets",
    )

    # Location assignment (GenericForeignKey to dcim Region/Site/Location)
    location_assigned_object_type = ContentTypeFilter()
    location_assigned_object_id = MultiValueNumberFilter()
    # Hierarchical shortcuts: everything placed on the object or anything below it
    region_id = MultiValueNumberFilter(method="filter_region", label="Region (ID), including descendants")
    site_id = MultiValueNumberFilter(method="filter_site", label="Site (ID), including its locations")
    location_id = MultiValueNumberFilter(method="filter_location", label="Location (ID), including descendants")

    class Meta:
        model = ExternalInventory
        fields = [
            "id",
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            "person_id",
            "person_name",
            "location_code",
            "location",
            "external_location_id",
            "department_code",
            "project_code",
            "user_name",
            "split_asset",
            "status",
            "asset_id",
            "has_assets",
            "location_assigned_object_type",
            "location_assigned_object_id",
            "region_id",
            "site_id",
            "location_id",
        ]

    def filter_region(self, queryset, name, value):
        return queryset.filter(location_assignment_q(Region, value))

    def filter_site(self, queryset, name, value):
        return queryset.filter(location_assignment_q(Site, value))

    def filter_location(self, queryset, name, value):
        return queryset.filter(location_assignment_q(Location, value))

    def filter_has_assets(self, queryset, name, value):
        """
        Filter External Inventory objects based on whether they have assigned assets.

        Args:
            queryset: The base queryset
            name: The filter field name
            value: Boolean - True for objects with assets, False for objects without assets

        Returns:
            Filtered queryset
        """
        if value is True:
            # Vrátí pouze External Inventory objekty, které mají alespoň jeden přiřazený asset
            return queryset.filter(assets__isnull=False).distinct()
        elif value is False:
            # Vrátí pouze External Inventory objekty, které nemají žádný přiřazený asset
            return queryset.filter(assets__isnull=True)
        else:
            # Pokud value není boolean, vrátí původní queryset
            return queryset

    def search(self, queryset, name, value):
        """Allow searching by various fields using a single search parameter."""
        if value is None or not value.strip():
            return queryset
        return queryset.filter(
            Q(inventory_number__icontains=value)
            | Q(name__icontains=value)
            | Q(serial_number__icontains=value)
            | Q(external_id__icontains=value)
            | Q(person_id__icontains=value)
            | Q(person_name__icontains=value)
            | Q(location_code__icontains=value)
            | Q(location__icontains=value)
            | Q(external_location_id__icontains=value)
            | Q(department_code__icontains=value)
            | Q(project_code__icontains=value)
            | Q(user_name__icontains=value)
            | Q(user_note__icontains=value)
        )
