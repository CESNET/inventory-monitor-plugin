import django_filters
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from inventory_monitor.models import Contract, Invoice
from inventory_monitor.helpers import get_currency_choices


class InvoiceFilterSet(NetBoxModelFilterSet):
    """
    A filter set for filtering invoices.

    This filter set provides various filters for searching and filtering invoices based on different criteria such as name,
    project, contract, price, and invoicing dates.

    Attributes:
        q (django_filters.CharFilter): A filter for searching invoices by name.
        tag (TagFilter): A filter for filtering invoices by tag.
        name (django_filters.CharFilter): A filter for exact match of invoice name.
        name__ic (django_filters.CharFilter): A filter for case-insensitive partial match of invoice name.
        name_internal (django_filters.CharFilter): A filter for case-insensitive partial match of internal invoice name.
        project (django_filters.CharFilter): A filter for case-insensitive partial match of project name.
        contract_id (django_filters.ModelMultipleChoiceFilter): A filter for filtering invoices by contract ID.
        contract (django_filters.ModelMultipleChoiceFilter): A filter for filtering invoices by contract name.
        price (django_filters.NumberFilter): A filter for filtering invoices by price.
        invoicing_start__gte (django_filters.DateFilter): A filter for filtering invoices with invoicing start date greater than or equal to a given date.
        invoicing_start__lte (django_filters.DateFilter): A filter for filtering invoices with invoicing start date less than or equal to a given date.
        invoicing_start (django_filters.DateFilter): A filter for filtering invoices with invoicing start date containing a given date.
        invoicing_end__gte (django_filters.DateFilter): A filter for filtering invoices with invoicing end date greater than or equal to a given date.
        invoicing_end__lte (django_filters.DateFilter): A filter for filtering invoices with invoicing end date less than or equal to a given date.
        invoicing_end (django_filters.DateFilter): A filter for filtering invoices with invoicing end date containing a given date.
    """

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="exact", field_name="name")
    name__ic = django_filters.CharFilter(field_name="name", lookup_expr="icontains", label="Name Contains")
    name_internal = django_filters.CharFilter(lookup_expr="icontains")
    project = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter()

    contract_id = django_filters.ModelMultipleChoiceFilter(
        field_name="contract__id",
        queryset=Contract.objects.all(),
        to_field_name="id",
        label="Contract (ID)",
    )
    contract = django_filters.ModelMultipleChoiceFilter(
        field_name="contract__name",
        queryset=Contract.objects.all(),
        to_field_name="name",
        label="Contract (name)",
    )

    # Price filters
    price = django_filters.NumberFilter(required=False)
    price__gte = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Price (min)",
    )
    price__lte = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Price (max)",
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

    invoicing_start__gte = django_filters.DateFilter(field_name="invoicing_start", lookup_expr="gte")
    invoicing_start__lte = django_filters.DateFilter(field_name="invoicing_start", lookup_expr="lte")
    invoicing_start = django_filters.DateFilter(field_name="invoicing_start", lookup_expr="contains")
    invoicing_end__gte = django_filters.DateFilter(field_name="invoicing_end", lookup_expr="gte")
    invoicing_end__lte = django_filters.DateFilter(field_name="invoicing_end", lookup_expr="lte")
    invoicing_end = django_filters.DateFilter(field_name="invoicing_end", lookup_expr="contains")

    class Meta:
        model = Invoice
        fields = (
            "id",
            "name",
            "name_internal",
            "project",
            "description",
            "contract",
            "price",
            "currency",
            "invoicing_start",
            "invoicing_end",
        )

    def search(self, queryset, name, value):
        """
        A method for searching invoices by name, internal name, or description.

        Args:
            queryset (QuerySet): The queryset to filter.
            name (str): The name of the filter.
            value (str): The value to search for.

        Returns:
            QuerySet: The filtered queryset.

        """
        name = Q(name__icontains=value)
        name_internal = Q(name_internal__icontains=value)
        description = Q(description__icontains=value)
        return queryset.filter(name | name_internal | description)
