import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

# Helper imports for custom columns and templates
from inventory_monitor.helpers import (
    CurrencyColumn,
    TEMPLATE_SERVICES_CONTRACTS,
    TEMPLATE_SERVICES_END,
)
from inventory_monitor.models import Asset


def _should_highlight_device_serial_match(record, table):
    """Helper to determine if asset serial should be highlighted."""
    # Early return if asset has no serial
    if not record.serial:
        return False

    # Get the device serial from the asset's assignment
    asset_device_serial = None

    if record.assigned_object:
        # Check if assigned to a Device directly
        if hasattr(record.assigned_object, "_meta") and record.assigned_object._meta.model_name == "device":
            asset_device_serial = record.assigned_object.serial

        # Check if assigned to a Module (which belongs to a Device)
        elif hasattr(record.assigned_object, "_meta") and record.assigned_object._meta.model_name == "module":
            # Module should have a device attribute
            if hasattr(record.assigned_object, "device") and record.assigned_object.device:
                asset_device_serial = record.assigned_object.device.serial

    # Compare the asset serial with its assigned device serial
    if asset_device_serial:
        return str(record.serial).strip().lower() == str(asset_device_serial).strip().lower()

    return False


ASSOCIATED_EXTERNAL_INVENTORY_ASSETS = """
  {% if value.count > 3 %}
    <a href="{% url 'plugins:inventory_monitor:externalinventory_list' %}?asset_id={{ record.pk }}">{{ value.count }}</a>
  {% else %}
    {% for item in value.all %}
        <a 
            href="{{ item.get_absolute_url }}" 
            class="badge text-bg-{{ item.get_status_color }}" 
            data-bs-toggle="tooltip" 
            data-bs-placement="left"
            style="
                white-space: normal;        /* povolí zalamování řádků */
                word-break: keep-all;       /* nezalomí slovo, jen mezi slovy */
                overflow-wrap: normal;      /* defaultní chování, zalamuje jen na mezerách */
                max-width: 200px;           /* nastavte podle potřeby */
                display: inline-block;      /* aby šířka fungovala */
            "
            title="{{ item.get_status_display }}"
        >
            {{ item.inventory_number }}: {{ item.name }}
        </a>
    {% endfor %}
  {% endif %}
"""


class AssetTable(NetBoxTable):
    """
    Table configuration for displaying Asset objects in list views
    """

    #
    # Basic identification columns
    #
    description = tables.Column()
    serial = tables.Column(linkify=True)
    partnumber = tables.Column()
    external_inventory_asset_numbers = tables.TemplateColumn(
        template_code="""
        {% if record.get_external_inventory_asset_numbers_display %}
            {{ record.get_external_inventory_asset_numbers_display }}
        {% else %}
            {{ ''|placeholder }}
        {% endif %}
        """,
        verbose_name="Asset Number(s)",
        orderable=False,
    )

    #
    # Type and classification columns
    #
    type = columns.TemplateColumn(
        template_code="""
        {% if record.type %}
            <a href="{{ record.type.get_absolute_url }}">
                {% if record.type.color %}
                    <span class="badge" style="background-color: #{{ record.type.color }}">
                        {{ record.type.name }}
                    </span>
                {% else %}
                    {{ record.type.name }}
                {% endif %}
            </a>
        {% endif %}
        """,
        verbose_name="Type",
        orderable=True,
    )

    #
    # Status columns
    #
    assignment_status = columns.ChoiceFieldColumn()
    lifecycle_status = columns.ChoiceFieldColumn()

    # Formatted column for warranty status using a template
    warranty_status = tables.TemplateColumn(
        template_code="""
            {% include 'inventory_monitor/inc/status_badge.html' with status_type='warranty' %}
        """,
        verbose_name="Warranty Status",
        orderable=False,
    )

    #
    # Assignment columns
    #
    assigned_object = tables.Column(verbose_name="Assigned Object", orderable=False, linkify=True)
    external_inventory_items = tables.TemplateColumn(
        template_code=ASSOCIATED_EXTERNAL_INVENTORY_ASSETS,
        orderable=False,
        verbose_name="External Inventory Items",
    )

    #
    # Related object columns
    #
    order_contract = tables.Column(linkify=True)

    #
    # Additional information columns
    #
    project = tables.Column()
    vendor = tables.Column()
    quantity = tables.Column()
    price = CurrencyColumn(price_field="price", currency_field="currency")

    #
    # Service information columns
    #
    services_to = columns.TemplateColumn(template_code=TEMPLATE_SERVICES_END, verbose_name="Service End")
    services_contracts = tables.TemplateColumn(
        template_code=TEMPLATE_SERVICES_CONTRACTS, verbose_name="Service Contracts"
    )

    #
    # Warranty information columns
    #
    warranty_start = tables.Column()
    warranty_end = tables.Column()

    #
    # Metadata columns
    #
    tags = columns.TagColumn()
    comments = tables.Column()

    class Meta(NetBoxTable.Meta):
        model = Asset

        # Define all available fields that can be displayed in the table
        fields = (
            # Key identifiers
            "pk",
            "id",
            "partnumber",
            # Basic identification
            "serial",
            "external_inventory_asset_numbers",
            "description",
            # Type and classification
            "type",
            # Status
            "assignment_status",
            "lifecycle_status",
            # Assignment
            "assigned_object",
            "external_inventory_items",
            # Additional information
            "project",
            "vendor",
            "quantity",
            "price",
            "currency",
            # Related objects
            "order_contract",
            # Warranty information
            "warranty_start",
            "warranty_end",
            "warranty_status",
            # Service information
            "services_count",
            "services_contracts",
            "services_to",
            # Metadata
            "comments",
            "tags",
            "actions",
        )

        # Define the default columns that are shown when the table first loads
        default_columns = (
            "id",
            "serial",
            "description",
            "type",
            "assignment_status",
            "lifecycle_status",
        )


class EnhancedAssetTable(AssetTable):
    """
    Enhanced Asset table with probe status and optional device serial matching.
    """

    def __init__(self, *args, device=None, **kwargs):
        self.device = device
        super().__init__(*args, **kwargs)

    # Add probe status columns
    last_probe_time = tables.TemplateColumn(
        template_code="""
        {% load tz %}
        {% with probe_time=record.get_last_probe_time %}
            {% if probe_time %}
                <span title="Last probed: {{ probe_time|date:'Y-m-d H:i:s' }}">
                    {{ probe_time|date:"Y-m-d H:i" }}
                </span>
            {% else %}
                <span class="text-muted" title="Never probed">Never</span>
            {% endif %}
        {% endwith %}
        """,
        verbose_name="Last Probe",
        orderable=False,
    )

    probe_status = tables.TemplateColumn(
        template_code="""
        {% if record.is_recently_probed %}
            <span class="badge text-bg-success" title="Probed within last 7 days">
                <i class="mdi mdi-check-circle"></i> Recent
            </span>
        {% else %}
            <span class="badge text-bg-secondary" title="Not probed recently or never">
                <i class="mdi mdi-clock-outline"></i> Stale
            </span>
        {% endif %}
        """,
        verbose_name="Probe Status",
        orderable=False,
    )

    class Meta(AssetTable.Meta):
        # Add row attributes for styling based on probe status - using data attributes for CSS targeting
        row_attrs = {
            "data-probe-status": lambda record: ("recent" if record.is_recently_probed() else "stale"),
            "data-serial": lambda record: record.serial,
            "serial-match-device": lambda record, table: (
                "true" if _should_highlight_device_serial_match(record, table) else "false"
            ),
        }

        # Include probe columns in the fields
        fields = AssetTable.Meta.fields + ("last_probe_time", "probe_status")

        # Enhanced default columns with probe information
        default_columns = (
            "id",
            "partnumber",
            "serial",
            "description",
            "type",
            "assigned_object",
            "assignment_status",
            "lifecycle_status",
            "probe_status",
            "last_probe_time",
            "actions",
        )
