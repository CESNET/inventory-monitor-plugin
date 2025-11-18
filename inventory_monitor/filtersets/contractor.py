import django_filters
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet
from tenancy.models import Tenant

from inventory_monitor.models import Contractor


class ContractorFilterSet(NetBoxModelFilterSet):
    """
    Filter set for the Contractor model.

    This filter set allows filtering the Contractor model based on various fields such as name, company, and address.
    It also provides a search method to perform a case-insensitive search across these fields.

    Attributes:
        q (django_filters.CharFilter): A filter for performing a search across multiple fields.
        tag (TagFilter): A filter for filtering by tags.
        name (django_filters.CharFilter): A filter for filtering by name (case-insensitive).
        company (django_filters.CharFilter): A filter for filtering by company (case-insensitive).
        address (django_filters.CharFilter): A filter for filtering by address (case-insensitive).

    Meta:
        model (Contractor): The Contractor model that this filter set is associated with.
        fields (tuple): The fields that can be used for filtering.

    Methods:
        search(queryset, name, value): A method for performing a case-insensitive search across the name, company, and address fields.

    """

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()

    name = django_filters.CharFilter(lookup_expr="icontains")
    company = django_filters.CharFilter(lookup_expr="icontains")
    address = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter()

    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name="tenant__id",
        queryset=Tenant.objects.all(),
        to_field_name="id",
        label="Tenant (ID)",
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name="tenant__name",
        queryset=Tenant.objects.all(),
        to_field_name="name",
        label="Tenant (name)",
    )

    class Meta:
        model = Contractor
        fields = ("id", "name", "company", "address", "description", "tenant")

    def search(self, queryset, name, value):
        """
        Perform a case-insensitive search across the name, company, address, and description fields.

        Args:
            queryset (QuerySet): The initial queryset to filter.
            name (str): The name of the search filter.
            value (str): The value to search for.

        Returns:
            QuerySet: The filtered queryset.

        """
        name = Q(name__icontains=value)
        company = Q(company__icontains=value)
        address = Q(address__icontains=value)
        description = Q(description__icontains=value)
        tenant_name = Q(tenant__name__icontains=value)
        return queryset.filter(name | company | address | description | tenant_name)
