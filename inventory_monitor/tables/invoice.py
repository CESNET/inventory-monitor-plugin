import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from inventory_monitor.helpers import CurrencyColumn
from inventory_monitor.models import Invoice


class InvoiceTable(NetBoxTable):
    name = tables.Column(linkify=True, verbose_name="Invoice Number")
    name_internal = tables.Column(verbose_name="Internal ID")
    contract = tables.Column(linkify=True)
    attachments_count = tables.Column()
    price = CurrencyColumn(price_field="price", currency_field="currency")
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Invoice
        fields = (
            "pk",
            "id",
            "name",
            "name_internal",
            "project",
            "contract",
            "price",
            "currency",
            "invoicing_start",
            "invoicing_end",
            "comments",
            "attachments_count",
            "actions",
            "tags",
        )
        default_columns = (
            "id",
            "name",
            "name_internal",
            "contract",
            "project",
            "invoicing_start",
            "invoicing_end",
            "price",
            "attachments_count",
        )
