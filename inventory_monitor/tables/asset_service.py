import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from inventory_monitor.helpers import CurrencyColumn
from inventory_monitor.models import AssetService


class AssetServiceTable(NetBoxTable):
    asset = tables.Column(linkify=True)
    contract = tables.Column(linkify=True)
    service_start = tables.Column(verbose_name="Service Start")
    service_end = tables.Column(verbose_name="Service End")
    service_price = CurrencyColumn(price_field="service_price", currency_field="service_currency")
    service_status = tables.TemplateColumn(
        template_code="""
            {% include 'inventory_monitor/inc/status_badge.html' with status_type='service' start_date=record.service_start end_date=record.service_end %}
        """,
        verbose_name="Service Status",
        orderable=False,
    )
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
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
