import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin

from inventory_monitor.models import Contractor


class ContractorTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(linkify=True)
    contracts_count = tables.Column()
    tenant = tables.Column(linkify=True)
    owner = tables.Column(linkify=True, verbose_name="Owner")
    owner_group = tables.Column(accessor="owner__group", linkify=True, verbose_name="Owner Group")
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Contractor
        fields = (
            "pk",
            "id",
            "name",
            "company",
            "address",
            "tenant",
            "comments",
            "contracts_count",
            "contacts",
            "owner",
            "owner_group",
            "actions",
        )
        default_columns = ("id", "name", "company", "tenant", "contracts_count")
