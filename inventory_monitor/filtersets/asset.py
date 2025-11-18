import django_filters
from core.models import ObjectType

# NetBox model imports
from dcim.models import Device, Location, Module, Rack, Site
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filters import (
    ContentTypeFilter,
    MultiValueNumberFilter,
)

from inventory_monitor.helpers import get_currency_choices
from inventory_monitor.models import Asset, AssetType, Contract, ExternalInventory


class AssetFilterSet(NetBoxModelFilterSet):
    """
    Filterset for Asset objects providing comprehensive search and filtering capabilities.
    """

    #
    # Basic search filters
    #
    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()

    #
    # Identification filters
    #
    description = django_filters.CharFilter(lookup_expr="icontains", field_name="description")
    serial = django_filters.CharFilter(lookup_expr="iexact", field_name="serial")
    partnumber = django_filters.CharFilter(field_name="partnumber")

    external_inventory_number = django_filters.CharFilter(
        field_name="external_inventory_items__inventory_number",
        label="External Inventory Asset Number",
        help_text="Filter by external inventory number",
    )

    #
    # Status filters
    #
    assignment_status = django_filters.MultipleChoiceFilter(
        choices=Asset.assignment_status.field.choices,
    )
    lifecycle_status = django_filters.MultipleChoiceFilter(
        choices=Asset.lifecycle_status.field.choices,
    )

    #
    # Assignment filters
    #
    assigned_object_type = ContentTypeFilter()
    assigned_object_id = MultiValueNumberFilter()

    #
    # Related object filters
    #
    type_id = django_filters.ModelMultipleChoiceFilter(
        required=False,
        field_name="type__id",
        queryset=AssetType.objects.all(),
        to_field_name="id",
        label="Type (ID)",
    )
    order_contract = django_filters.ModelMultipleChoiceFilter(
        field_name="order_contract__id",
        queryset=Contract.objects.all(),
        to_field_name="id",
        label="Order Contract (ID)",
    )
    external_inventory_items = django_filters.ModelMultipleChoiceFilter(
        field_name="external_inventory_items__id",
        queryset=ExternalInventory.objects.all(),
        to_field_name="id",
        label="External Inventory (ID)",
    )

    has_external_inventory_items = django_filters.BooleanFilter(
        method="filter_has_external_inventory_items",
        label="Has External Inventory items",
    )

    #
    # Additional information filters
    #
    project = django_filters.CharFilter(lookup_expr="icontains")
    vendor = django_filters.CharFilter(lookup_expr="icontains", field_name="vendor")

    # Price range filters
    price = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="exact",
    )
    price__gte = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="gte",
    )
    price__lte = django_filters.NumberFilter(
        required=False,
        field_name="price",
        lookup_expr="lte",
    )
    price__isnull = django_filters.BooleanFilter(
        field_name="price",
        lookup_expr="isnull",
        label="Price is not set",
    )

    currency = django_filters.MultipleChoiceFilter(choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config
        self.filters["currency"].field.choices = get_currency_choices()

    # Quantity range filters
    quantity = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="exact",
    )
    quantity__gte = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="gte",
    )
    quantity__lte = django_filters.NumberFilter(
        required=False,
        field_name="quantity",
        lookup_expr="lte",
    )

    #
    # Warranty filters
    #
    warranty_start = django_filters.DateFilter(field_name="warranty_start", lookup_expr="contains")
    warranty_start__gte = django_filters.DateFilter(field_name="warranty_start", lookup_expr="gte")
    warranty_start__lte = django_filters.DateFilter(field_name="warranty_start", lookup_expr="lte")
    warranty_end = django_filters.DateFilter(field_name="warranty_end", lookup_expr="contains")
    warranty_end__gte = django_filters.DateFilter(field_name="warranty_end", lookup_expr="gte")
    warranty_end__lte = django_filters.DateFilter(field_name="warranty_end", lookup_expr="lte")

    class Meta:
        model = Asset
        fields = (
            "id",
            "partnumber",
            "serial",
            "description",
            "assignment_status",
            "lifecycle_status",
            "project",
            "vendor",
            "price",
            "currency",
            "order_contract",
            "warranty_start",
            "warranty_end",
            "has_external_inventory_items",
            "external_inventory_number",
        )

    def filter_has_external_inventory_items(self, queryset, name, value):
        """
        Filter assets based on whether they have external inventory items.

        Uses exclude for the false case to avoid join-induced duplicates.
        """
        if value is True:
            return queryset.filter(external_inventory_items__isnull=False).distinct()
        elif value is False:
            return queryset.exclude(external_inventory_items__isnull=False)
        else:
            return queryset

    def search(self, queryset, name, value):
        """
        Perform global search across multiple fields and related objects

        Searches through:
        - Asset fields (description, serial, project, vendor)
        - Related order contract names
        - Assigned objects (devices, sites, locations, racks)
        - External Inventory numbers

        Args:
            queryset: Base queryset to filter
            name: Name of the filter parameter
            value: Search term to filter by

        Returns:
            Filtered queryset containing matching assets
        """
        # Basic field searches
        description_search = Q(description__icontains=value)
        serial = Q(serial__icontains=value)
        partnumber = Q(partnumber__icontains=value)
        project = Q(project__icontains=value)
        vendor = Q(vendor__icontains=value)
        order_contract = Q(order_contract__name__icontains=value)

        # Add External Inventory inventory number search
        external_inventory_number = Q(external_inventory_items__inventory_number__icontains=value)

        # Get object types for assigned object types
        device_type = ObjectType.objects.get_for_model(Device)
        site_type = ObjectType.objects.get_for_model(Site)
        location_type = ObjectType.objects.get_for_model(Location)
        rack_type = ObjectType.objects.get_for_model(Rack)
        module_type = ObjectType.objects.get_for_model(Module)

        # Search through assigned objects
        device_search = Q(
            assigned_object_type=device_type,
            assigned_object_id__in=Device.objects.filter(name__icontains=value).values_list("pk", flat=True),
        )
        site_search = Q(
            assigned_object_type=site_type,
            assigned_object_id__in=Site.objects.filter(name__icontains=value).values_list("pk", flat=True),
        )
        location_search = Q(
            assigned_object_type=location_type,
            assigned_object_id__in=Location.objects.filter(name__icontains=value).values_list("pk", flat=True),
        )
        rack_search = Q(
            assigned_object_type=rack_type,
            assigned_object_id__in=Rack.objects.filter(name__icontains=value).values_list("pk", flat=True),
        )
        module_search = Q(
            assigned_object_type=module_type,
            assigned_object_id__in=Module.objects.filter(
                Q(description__icontains=value) | Q(serial__icontains=value) | Q(asset_tag__icontains=value)
            ).values_list("pk", flat=True),
        )

        # Combine all search conditions including External Inventory numbers
        return queryset.filter(
            description_search
            | serial
            | partnumber
            | project
            | vendor
            | order_contract
            | external_inventory_number
            | device_search
            | site_search
            | location_search
            | rack_search
            | module_search
        ).distinct()
