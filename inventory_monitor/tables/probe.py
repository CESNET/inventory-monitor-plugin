import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from inventory_monitor.models import Probe


def _compare_serials(serial1, serial2):
    """
    Helper function to compare two serial numbers with normalized whitespace.

    Args:
        serial1: First serial number to compare
        serial2: Second serial number to compare

    Returns:
        bool: True if serials match after normalization, False otherwise
    """
    if not serial1 or not serial2:
        return False
    return str(serial1).strip() == str(serial2).strip()


def _should_highlight_serial_match(record, table):
    """Helper to determine if probe serial should be highlighted."""
    # For asset probe views
    if (
        hasattr(table, "asset")
        and table.asset
        and table.asset.assigned_object
        and hasattr(table.asset.assigned_object, "serial")
        and table.asset.assigned_object.serial
        and record.serial
    ):
        return _compare_serials(record.serial, table.asset.assigned_object.serial)

    # For device probe views (if needed)
    if hasattr(table, "device") and table.device and table.device.serial and record.serial:
        return _compare_serials(record.serial, table.device.serial)

    # For regular probe views (probe serial vs its own device)
    if record.serial and record.device and hasattr(record.device, "serial") and record.device.serial:
        return _compare_serials(record.serial, record.device.serial)

    return False


class ProbeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    changes_count = tables.Column(orderable=False)
    discovered_data = tables.JSONColumn()
    tags = columns.TagColumn()

    class Meta(NetBoxTable.Meta):
        model = Probe
        fields = (
            "pk",
            "id",
            "time",
            "name",
            "device_descriptor",
            "site_descriptor",
            "location_descriptor",
            "description",
            "part",
            "serial",
            "device",
            "site",
            "location",
            "comments",
            "changes_count",
            "actions",
            "category",
            "creation_time",
        )
        default_columns = (
            "id",
            "time",
            "creation_time",
            "name",
            "serial",
            "part",
            "device",
            "site",
            "location",
            "changes_count",
        )

        # Add row attributes for styling based on probe status - using data attributes for CSS targeting
        row_attrs = {
            "data-probe-status": lambda record: "recent" if record.is_recently_probed() else "stale",
            "data-serial": lambda record: record.serial,
        }


class EnhancedProbeTable(ProbeTable):
    """
    Enhanced Probe table with probe status, timing, and optional serial matching.
    """

    def __init__(self, *args, asset=None, device=None, **kwargs):
        self.asset = asset
        self.device = device
        super().__init__(*args, **kwargs)

    # Add probe status column
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

    # Enhanced time display
    time_display = tables.TemplateColumn(
        template_code="""
        {% load tz %}
        {% if record.time %}
            <span title="Last probed: {{ record.time|date:'Y-m-d H:i:s' }}">
                {{ record.time|date:"Y-m-d H:i" }}
            </span>
            <br>
            <small class="text-muted">{{ record.time|timesince }} ago</small>
        {% else %}
            <span class="text-muted" title="Never probed">Never</span>
        {% endif %}
        """,
        verbose_name="Last Probe Time",
        orderable=True,
        order_by="time",
    )

    class Meta(ProbeTable.Meta):
        # Include enhanced columns in the fields
        fields = ProbeTable.Meta.fields + ("probe_status", "time_display")

        # Enhanced default columns with probe status information
        default_columns = (
            "id",
            "time_display",
            "creation_time",
            "name",
            "serial",
            "part",
            "device",
            "site",
            "location",
            "probe_status",
            "changes_count",
        )

        row_attrs = {
            **ProbeTable.Meta.row_attrs,
            "serial-match-device": lambda record, table: (
                "true" if _should_highlight_serial_match(record, table) else "false"
            ),
        }
