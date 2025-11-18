from netbox.plugins import PluginConfig

from .version import __version__


class NetBoxInventoryMonitorConfig(PluginConfig):
    name = "inventory_monitor"
    verbose_name = " Inventory Monitor"
    description = "Manage inventory discovered by SNMP"
    version = __version__
    base_url = "inventory-monitor"

    default_settings = {
        # Probe Status Settings
        "probe_recent_days": 7,
        # Currency Settings
        "currencies": [
            ("CZK", "Czech Koruna", "Kč"),
            ("EUR", "Euro", "€"),
            ("USD", "US Dollar", "$"),
            ("GBP", "British Pound", "£"),
            ("JPY", "Japanese Yen", "¥"),
        ],
        "default_currency": "EUR",
    }
    required_settings = []
    min_version = "4.4.0"
    max_version = "4.4.99"


config = NetBoxInventoryMonitorConfig
