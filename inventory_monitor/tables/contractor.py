import django_tables2 as tables
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin

from inventory_monitor.models import Contractor


class ContractorTable(ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(linkify=True)
    contracts_count = tables.Column()
    tenant = tables.Column(linkify=True)
    tags = columns.TagColumn()

    class Meta(PrimaryModelTable.Meta):
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
