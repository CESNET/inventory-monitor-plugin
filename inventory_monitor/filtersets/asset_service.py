import django_filters
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from inventory_monitor.models import Asset, AssetService, Contract


class AssetServiceFilterSet(NetBoxModelFilterSet):
    """
    Filter set for AssetService model.

    This filter set provides filtering options for various fields of the AssetService model,
    such as service start date, service end date, service parameter, service price, service category,
    service category vendor, asset, and contract.

    Attributes:
        q (django_filters.CharFilter): Filter for searching by a specific value.
        tag (TagFilter): Filter for filtering by tags.
        service_start (django_filters.DateFilter): Filter for filtering by service start date.
        service_start__gte (django_filters.DateFilter): Filter for filtering by service start date greater than or equal to a specific value.
        service_start__lte (django_filters.DateFilter): Filter for filtering by service start date less than or equal to a specific value.
        service_end (django_filters.DateFilter): Filter for filtering by service end date.
        service_end__gte (django_filters.DateFilter): Filter for filtering by service end date greater than or equal to a specific value.
        service_end__lte (django_filters.DateFilter): Filter for filtering by service end date less than or equal to a specific value.
        service_price (django_filters.NumberFilter): Filter for filtering by service price.
        service_price__gte (django_filters.NumberFilter): Filter for filtering by service price greater than or equal to a specific value.
        service_price__lte (django_filters.NumberFilter): Filter for filtering by service price less than or equal to a specific value.
        service_category (django_filters.CharFilter): Filter for filtering by service category.
        service_category_vendor (django_filters.CharFilter): Filter for filtering by service category vendor.
        asset (django_filters.ModelMultipleChoiceFilter): Filter for filtering by asset.
        contract (django_filters.ModelMultipleChoiceFilter): Filter for filtering by contract.

    Methods:
        search(queryset, name, value): Custom method for searching across multiple fields.

    """

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    service_start = django_filters.DateFilter(field_name="service_start", lookup_expr="contains")
    service_start__gte = django_filters.DateFilter(field_name="service_start", lookup_expr="gte")
    service_start__lte = django_filters.DateFilter(field_name="service_start", lookup_expr="lte")
    service_end = django_filters.DateFilter(field_name="service_end", lookup_expr="contains")
    service_end__gte = django_filters.DateFilter(field_name="service_end", lookup_expr="gte")
    service_end__lte = django_filters.DateFilter(field_name="service_end", lookup_expr="lte")
    service_price = django_filters.NumberFilter(
        required=False,
        field_name="service_price",
        lookup_expr="exact",
    )
    service_price = django_filters.NumberFilter(
        field_name="service_price",
        label="Service Price",
    )
    service_price__gte = django_filters.NumberFilter(
        required=False,
        field_name="service_price",
        lookup_expr="gte",
    )
    service_price__lte = django_filters.NumberFilter(
        required=False,
        field_name="service_price",
        lookup_expr="lte",
    )
    service_price__isnull = django_filters.BooleanFilter(
        field_name="service_price",
        lookup_expr="isnull",
        label="Service Price is not set",
    )
    service_category = django_filters.CharFilter(lookup_expr="icontains", field_name="service_category")
    service_category_vendor = django_filters.CharFilter(lookup_expr="icontains", field_name="service_category_vendor")
    description = django_filters.CharFilter()
    service_currency = django_filters.MultipleChoiceFilter(
        choices=[],
        label="Service Currency",
    )
    asset = django_filters.ModelMultipleChoiceFilter(
        field_name="asset__id",
        queryset=Asset.objects.all(),
        to_field_name="id",
        label="Asset (ID)",
    )
    contract = django_filters.ModelMultipleChoiceFilter(
        field_name="contract__id",
        queryset=Contract.objects.all(),
        to_field_name="id",
        label="Contract (ID)",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from inventory_monitor.helpers import get_currency_choices

        # Set currency choices dynamically from plugin config
        self.filters["service_currency"].field.choices = get_currency_choices()

    class Meta:
        model = AssetService
        fields = (
            "id",
            "service_start",
            "service_end",
            "service_price",
            "service_currency",
            "service_category",
            "service_category_vendor",
            "description",
            "asset",
            "contract",
        )

    def search(self, queryset, name, value):
        """
        Custom method for searching across multiple fields.

        Args:
            queryset (QuerySet): The initial queryset.
            name (str): The name of the field to search.
            value (str): The value to search for.

        Returns:
            QuerySet: The filtered queryset based on the search value.

        """
        service_category = Q(service_category__icontains=value)
        service_category_vendor = Q(service_category_vendor__icontains=value)
        description = Q(description__icontains=value)
        asset = Q(asset__serial__icontains=value)
        contract = Q(contract__name__icontains=value)
        return queryset.filter(service_category | service_category_vendor | description | asset | contract)
