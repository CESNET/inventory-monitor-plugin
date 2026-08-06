import django_tables2 as tables
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin

from inventory_monitor.models import RMA


class RMATable(ContactsColumnMixin, PrimaryModelTable):
    rma_number = tables.Column(linkify=True)
    asset = tables.Column(linkify=True)
    status = columns.ChoiceFieldColumn()
    tags = columns.TagColumn()

    class Meta(PrimaryModelTable.Meta):
        model = RMA
        fields = (
            "pk",
            "id",
            "rma_number",
            "asset",
            "original_serial",
            "replacement_serial",
            "status",
            "date_issued",
            "date_replaced",
            "issue_description",
            "vendor_response",
            "contacts",
            "owner",
            "owner_group",
            "actions",
        )
        default_columns = (
            "id",
            "rma_number",
            "asset",
            "original_serial",
            "replacement_serial",
            "status",
            "date_issued",
            "date_replaced",
            "actions",
        )
