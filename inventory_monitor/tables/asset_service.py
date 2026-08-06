import django_tables2 as tables
from netbox.tables import PrimaryModelTable, columns
from tenancy.tables import ContactsColumnMixin

from inventory_monitor.helpers import TEMPLATE_SERVICE_END, CachedTemplateColumn, CurrencyColumn, DateBadgeColumn
from inventory_monitor.models import AssetService


class AssetServiceTable(ContactsColumnMixin, PrimaryModelTable):
    asset = tables.Column(linkify=True)
    contract = tables.Column(linkify=True)
    # DateColumn renders ISO 8601; a plain Column would hand the date object to
    # the template, which localizes it to "June 3, 2022".
    service_start = columns.DateColumn(verbose_name="Service Start")
    service_end = DateBadgeColumn(
        template_code=TEMPLATE_SERVICE_END,
        verbose_name="Service End",
        order_by="service_end",
    )
    service_price = CurrencyColumn(price_field="service_price", currency_field="service_currency")
    service_status = CachedTemplateColumn(
        template_code="""
            {% include 'inventory_monitor/inc/status_badge.html' with status_type='service' start_date=record.service_start end_date=record.service_end %}
        """,
        verbose_name="Service Status",
        orderable=False,
    )
    tags = columns.TagColumn()

    class Meta(PrimaryModelTable.Meta):
        model = AssetService
        fields = (
            "pk",
            "id",
            "service_start",
            "service_end",
            "service_status",
            "service_price",
            "service_currency",
            "service_category",
            "service_category_vendor",
            "asset",
            "contract",
            "tags",
            "comments",
            "contacts",
            "owner",
            "owner_group",
            "actions",
        )
        default_columns = (
            "id",
            "contract",
            "service_status",
            "service_price",
            "service_category",
            "service_category_vendor",
            "tags",
            "actions",
        )
