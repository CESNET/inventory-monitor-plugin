"""
Plugin Settings Helper Module for Inventory Monitor Plugin.

This module provides centralized access to plugin configuration settings
and helper functions for commonly used settings.
"""

from django.conf import settings


def get_plugin_settings():
    """
    Get all plugin configuration settings.

    Returns:
        dict: Plugin configuration settings dictionary
    """
    return settings.PLUGINS_CONFIG.get("inventory_monitor", {})


def get_probe_recent_days():
    """
    Get the number of days to consider a probe "recent".

    Returns:
        int: Number of days (default: 7)
    """
    return get_plugin_settings().get("probe_recent_days", 7)


def get_external_inventory_status_config():
    """
    Get the external inventory status configuration.
    Returns empty dict if not configured.

    Returns:
        dict: Status configuration with codes, labels, and colors
    """
    return get_plugin_settings().get("external_inventory_status_config", {})


def get_external_inventory_status_config_safe():
    """
    Safely get external inventory status configuration with validation.
    Checks if configuration exists and is not empty.

    Returns:
        tuple: (config_dict, is_configured)
            - config_dict: Status configuration dictionary
            - is_configured: Boolean indicating if valid configuration exists
    """
    plugin_settings = get_plugin_settings()

    # Check if config key exists
    if "external_inventory_status_config" not in plugin_settings:
        return {}, False

    # Get the configuration
    status_config = plugin_settings.get("external_inventory_status_config", {})

    # Check if configuration is not empty
    if not status_config:
        return {}, False

    return status_config, True


def get_external_inventory_tooltip_template():
    """
    Get the configurable tooltip template for external inventory status.

    Returns:
        str: Template string for the tooltip content
    """
    default_template = "<span class='badge text-bg-{color}'>{code}</span> {label}"
    return get_plugin_settings().get("external_inventory_tooltip_template", default_template)


def get_warning_days(attribute):
    """
    Get the warning days threshold for a specific attribute.

    Args:
        attribute: The attribute key (e.g., "service", "warranty")

    Returns:
        int or None: Number of warning days, or None if not configured
                     (which means no color indicators should be shown)
    """
    warning_days = get_plugin_settings().get("warning_days", {})
    if not isinstance(warning_days, dict):
        return None
    return warning_days.get(attribute)


# Convenience constants using the settings functions
PLUGIN_SETTINGS = get_plugin_settings()
