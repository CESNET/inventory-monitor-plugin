import django_tables2 as tables
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin

from inventory_monitor.helpers import CurrencyColumn, TEMPLATE_INVOICING_STATUS
from inventory_monitor.models import Invoice


class InvoiceTable(ContactsColumnMixin, PrimaryModelTable):
    name = tables.Column(linkify=True, verbose_name="Invoice Number")
    name_internal = tables.Column(verbose_name="Internal ID")
    contract = tables.Column(linkify=True)
    attachments_count = tables.Column()
    price = CurrencyColumn(price_field="price", currency_field="currency")
    invoicing_status = tables.TemplateColumn(
        template_code=TEMPLATE_INVOICING_STATUS, verbose_name="Invoicing Status", orderable=False
    )
    tags = columns.TagColumn()

    class Meta(PrimaryModelTable.Meta):
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
            "invoicing_status",
            "comments",
            "attachments_count",
            "contacts",
            "owner",
            "owner_group",
            "actions",
            "tags",
        )
        default_columns = (
            "id",
            "name",
            "name_internal",
            "contract",
            "project",
            "invoicing_status",
            "price",
            "attachments_count",
        )
