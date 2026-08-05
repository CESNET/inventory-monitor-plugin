from core.models import ObjectType
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from inventory_monitor.settings import (
    get_external_inventory_status_config_safe,
    get_external_inventory_tooltip_template,
)

register = template.Library()


@register.filter
def get_status(obj, status_type):
    """
    Gets the status for the given object and status type
    Example: {{ record|get_status:'warranty' }} calls record.get_warranty_status()
    """
    method_name = f"get_{status_type}_status"
    if hasattr(obj, method_name):
        return getattr(obj, method_name)()
    return None


@register.simple_tag
def external_inventory_status_tooltip():
    """
    Generate a configurable status tooltip for external inventory.
    Returns empty string if no configuration is provided.

    Returns:
        str: HTML tooltip content based on plugin configuration, or empty string
    """
    # Use the centralized safe configuration access
    status_config, is_configured = get_external_inventory_status_config_safe()

    if not is_configured:
        return ""

    tooltip_template = get_external_inventory_tooltip_template()

    tooltip_parts = []
    for code, config in status_config.items():
        part = tooltip_template.format(code=code, label=_(config["label"]), color=config["color"])
        tooltip_parts.append(part)

    return mark_safe("<br/>".join(tooltip_parts))


@register.filter
def get_content_type_param(obj):
    """
    Returns the appropriate query parameter name for the given object.
    Example: For a Device object, returns 'device'
    """
    if obj is None:
        return None

    # Get the model name in lowercase
    object_type = ObjectType.objects.get_for_model(obj)
    model_name = object_type.model.lower()

    # You can customize this mapping if needed
    param_mapping = {
        # 'custommodelname': 'custom_param_name',
    }

    # Return the mapped param name or the model name by default
    return param_mapping.get(model_name, model_name)
