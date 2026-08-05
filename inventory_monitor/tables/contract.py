import django_tables2 as tables
from netbox.tables import ChoiceFieldColumn, NetBoxTable, columns
from tenancy.tables import ContactsColumnMixin

from inventory_monitor.helpers import CurrencyColumn, TEMPLATE_INVOICING_STATUS
from inventory_monitor.models import Contract


class ContractTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(linkify=True)
    contractor = tables.Column(linkify=True)
    subcontracts_count = tables.Column()
    invoices_count = tables.Column()
    contract_type = tables.Column(orderable=False)
    attachments_count = tables.Column()
    parent = tables.Column(linkify=True)
    type = ChoiceFieldColumn()
    price = CurrencyColumn(price_field="price", currency_field="currency")
    currency = tables.Column()
    invoicing_status = tables.TemplateColumn(
        template_code=TEMPLATE_INVOICING_STATUS, verbose_name="Invoicing Status", orderable=False
    )
    owner = tables.Column(linkify=True, verbose_name="Owner")
    owner_group = tables.Column(accessor="owner__group", linkify=True, verbose_name="Owner Group")
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Contract
        fields = (
            "pk",
            "id",
            "name",
            "name_internal",
            "contractor",
            "type",
            "contract_type",
            "price",
            "currency",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
            "invoicing_status",
            "parent",
            "comments",
            "invoices_count",
            "subcontracts_count",
            "attachments_count",
            "contacts",
            "owner",
            "owner_group",
            "actions",
        )
        default_columns = (
            "id",
            "name",
            "contractor",
            "type",
            "price",
            "invoicing_status",
        )
