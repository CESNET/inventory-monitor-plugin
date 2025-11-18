import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from inventory_monitor.models import ExternalInventory

ASSOCIATED_ASSETS = """
  {% if value and value.count > 3 %}
    <a href="{% url 'plugins:inventory_monitor:asset_list' %}?external_inventory_items={{ record.pk }}">{{ value.count }}</a>
  {% elif value and value.all %}
    {% for asset in value.all %}
      <a 
            href="{{ asset.get_absolute_url }}" 
            class="badge text-bg-{{ asset.get_lifecycle_status_color }}" 
            data-bs-toggle="tooltip" 
            data-bs-placement="left" 
            style="
                white-space: normal;        /* povolí zalamování řádků */
                word-break: keep-all;       /* nezalomí slovo, jen mezi slovy */
                overflow-wrap: normal;      /* defaultní chování, zalamuje jen na mezerách */
                max-width: 200px;           /* nastavte podle potřeby */
                display: inline-block;      /* aby šířka fungovala */            
            "
            title="{{ asset.get_lifecycle_status_display }}"
        >{{ asset }}</a>
    {% endfor %}
  {% endif %}
"""


class ExternalInventoryTable(NetBoxTable):
    """
    Table configuration for displaying External Inventory objects in list views
    """

    external_id = tables.Column(linkify=True)  # Add this field
    inventory_number = tables.Column(linkify=True)
    name = tables.Column()
    serial_number = tables.Column()
    person_name = tables.Column()
    location = tables.Column()
    status = tables.TemplateColumn(
        template_code="""
        {% if record.status %}
            <span class="badge text-bg-{{ record.get_status_color }}">
                {{ record.get_status_display }}
            </span>
        {% else %}
            {{ ''|placeholder }}
        {% endif %}
        """,
        verbose_name="Status",
    )
    assets = tables.TemplateColumn(template_code=ASSOCIATED_ASSETS, orderable=False, verbose_name="Assets")
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = ExternalInventory
        fields = (
            "pk",
            "id",
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            "person_id",
            "person_name",
            "location_code",
            "location",
            "department_code",
            "project_code",
            "user_name",
            "split_asset",
            "status",
            "tags",
            "assets",
            "actions",
        )
        default_columns = (
            "id",
            "external_id",
            "inventory_number",
            "name",
            "serial_number",
            "person_name",
            "location",
            "status",
            "tags",
            "assets",
            "actions",
        )
