import django_filters
from django.db.models import Q
from extras.filters import TagFilter
from netbox.filtersets import NetBoxModelFilterSet

from inventory_monitor.models import Contract, Contractor, ContractTypeChoices


class ContractFilterSet(NetBoxModelFilterSet):
    """
    Filter set for the Contract model.

    This filter set provides filters for various fields of the Contract model,
    such as name, contractor, type, price, signed date, accepted date, invoicing start date,
    invoicing end date, parent contract, and contract type.

    Available Filters:
    - q: Search filter for name and name_internal fields.
    - tag: Filter by tag.
    - name: Filter by exact match of the name field.
    - name__ic: Filter by case-insensitive partial match of the name field.
    - name_internal: Filter by case-insensitive partial match of the name_internal field.
    - contractor_id: Filter by contractor ID.
    - contractor: Filter by contractor name.
    - type: Filter by contract type.
    - price: Filter by contract price.
    - signed__gte: Filter by signed date greater than or equal to a given date.
    - signed__lte: Filter by signed date less than or equal to a given date.
    - signed: Filter by signed date containing a given date.
    - accepted__gte: Filter by accepted date greater than or equal to a given date.
    - accepted__lte: Filter by accepted date less than or equal to a given date.
    - accepted: Filter by accepted date containing a given date.
    - invoicing_start__gte: Filter by invoicing start date greater than or equal to a given date.
    - invoicing_start__lte: Filter by invoicing start date less than or equal to a given date.
    - invoicing_start: Filter by invoicing start date containing a given date.
    - invoicing_end__gte: Filter by invoicing end date greater than or equal to a given date.
    - invoicing_end__lte: Filter by invoicing end date less than or equal to a given date.
    - invoicing_end: Filter by invoicing end date containing a given date.
    - parent_id: Filter by parent contract ID.
    - parent: Filter by parent contract name.
    - contract_type: Filter by contract type (All, Contract, Subcontract).
    - master_contracts: Filter by master contracts only.

    """

    # Rest of the code...

    q = django_filters.CharFilter(
        method="search",
        label="Search",
    )
    tag = TagFilter()
    name = django_filters.CharFilter(lookup_expr="exact", field_name="name")
    name__ic = django_filters.CharFilter(field_name="name", lookup_expr="icontains", label="Name Contains")
    name_internal = django_filters.CharFilter(lookup_expr="icontains")
    description = django_filters.CharFilter()
    contractor_id = django_filters.ModelMultipleChoiceFilter(
        field_name="contractor__id",
        queryset=Contractor.objects.all(),
        to_field_name="id",
        label="Contractor (ID)",
    )
    contractor = django_filters.ModelMultipleChoiceFilter(
        field_name="contractor__name",
        queryset=Contractor.objects.all(),
        to_field_name="name",
        label="Contractor (name)",
    )

    type = django_filters.MultipleChoiceFilter(choices=ContractTypeChoices, required=False)

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
    currency = django_filters.MultipleChoiceFilter(
        choices=[],
        label="Currency",
    )
    signed__gte = django_filters.DateFilter(field_name="signed", lookup_expr="gte")
    signed__lte = django_filters.DateFilter(field_name="signed", lookup_expr="lte")
    signed = django_filters.DateFilter(field_name="signed", lookup_expr="contains")
    accepted__gte = django_filters.DateFilter(field_name="accepted", lookup_expr="gte")
    accepted__lte = django_filters.DateFilter(field_name="accepted", lookup_expr="lte")
    accepted = django_filters.DateFilter(field_name="accepted", lookup_expr="contains")
    invoicing_start__gte = django_filters.DateFilter(field_name="invoicing_start", lookup_expr="gte")
    invoicing_start__lte = django_filters.DateFilter(field_name="invoicing_start", lookup_expr="lte")
    invoicing_start = django_filters.DateFilter(field_name="invoicing_start", lookup_expr="contains")
    invoicing_end__gte = django_filters.DateFilter(field_name="invoicing_end", lookup_expr="gte")
    invoicing_end__lte = django_filters.DateFilter(field_name="invoicing_end", lookup_expr="lte")
    invoicing_end = django_filters.DateFilter(field_name="invoicing_end", lookup_expr="contains")
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name="parent__id",
        queryset=Contract.objects.all(),
        to_field_name="id",
        label="Contract (ID)",
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name="parent__name",
        queryset=Contract.objects.all(),
        to_field_name="name",
        label="Contract (name)",
    )
    contract_type = django_filters.MultipleChoiceFilter(
        choices=(
            ("All", "All"),
            ("Contract", "Contract"),
            ("Subcontract", "Subcontract"),
        ),
        required=False,
        label="Contract type",
        method="_contract_type",
    )

    master_contracts = django_filters.BooleanFilter(method="_master_contracts", label="Master contracts only")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from inventory_monitor.helpers import get_currency_choices

        # Set currency choices dynamically from plugin config
        self.filters["currency"].field.choices = get_currency_choices()

    class Meta:
        model = Contract
        fields = (
            "id",
            "name",
            "name_internal",
            "description",
            "contractor",
            "type",
            "price",
            "currency",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
        )

    def search(self, queryset, name, value):
        name = Q(name__icontains=value)
        name_internal = Q(name_internal__icontains=value)
        description = Q(description__icontains=value)
        return queryset.filter(name | name_internal | description)

    def _master_contracts(self, queryset, name, value):
        if value:
            return queryset.filter(parent=None)
        else:
            return queryset

    def _contract_type(self, queryset, name, value):
        if value == ["All"]:
            return queryset
        elif value == ["Contract"]:
            return queryset.filter(parent=None)
        elif value == ["Subcontract"]:
            return queryset.exclude(parent=None)
        else:
            return queryset
