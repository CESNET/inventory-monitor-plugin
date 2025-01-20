from netbox.plugins import PluginConfig
from .version import __version__


class NetBoxInventoryMonitorConfig(PluginConfig):
    name = "inventory_monitor"
    verbose_name = " Inventory Monitor"
    description = "Manage inventory discovered by SNMP"
    version = __version__
    base_url = "inventory-monitor"

    default_settings = {}
    required_settings = []
    min_version = '4.2.0'
    max_version = '4.2.99'


config = NetBoxInventoryMonitorConfig
