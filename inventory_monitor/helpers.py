import functools
import importlib.metadata
import logging

import django_tables2
from core.models import ObjectType
from django.db.models import Count, OuterRef, Subquery, Value
from netbox.plugins import get_plugin_config
from packaging.version import Version
from utilities.templatetags.builtins.filters import register

logger = logging.getLogger("inventory_monitor")


def get_currency_choices():
    """Get currency choices from plugin configuration.

    Returns list of tuples: (code, name) for form choices.
    Validates each entry to prevent errors from malformed config.
    """
    currencies = get_plugin_config("inventory_monitor", "currencies", [])
    # Return tuples of (code, name) - validate and strip symbol if present
    choices = []
    for c in currencies:
        # Validate entry format: must be list/tuple with at least 2 non-empty elements
        if isinstance(c, (list, tuple)) and len(c) >= 2 and c[0] and c[1]:
            choices.append((c[0], c[1]))
    return choices


def get_default_currency():
    """Get default currency from plugin configuration."""
    return get_plugin_config("inventory_monitor", "default_currency", "EUR")


def get_currency_symbol(currency_code):
    """Get currency symbol from plugin configuration.

    Args:
        currency_code: Currency code (e.g., 'CZK', 'EUR')

    Returns:
        Currency symbol if configured, otherwise the currency code itself
    """
    if not currency_code:
        return ""

    currencies = get_plugin_config("inventory_monitor", "currencies", [])

    # Look for currency in config
    for currency in currencies:
        # Validate entry format before accessing
        if not isinstance(currency, (list, tuple)) or len(currency) < 2:
            continue

        if currency[0] == currency_code:
            # Return symbol if it's a 3-tuple (code, name, symbol) and symbol is not empty
            if len(currency) >= 3 and currency[2]:
                return currency[2]
            # Otherwise return the code
            return currency_code

    # Fallback to code if not found
    return currency_code


def get_object_type_or_none(app_label, model):
    try:
        object_type = ObjectType.objects.get(app_label=app_label, model=model)
        return object_type
    except Exception:
        return None


@functools.cache
def _get_attachment_model():
    """Return NetBoxAttachmentAssignment model class if available, None otherwise."""
    if not get_plugin_config("inventory_monitor", "enable_netbox_attachments", False):
        return None

    try:
        installed = importlib.metadata.version("netbox-attachments")
    except importlib.metadata.PackageNotFoundError:
        logger.error("enable_netbox_attachments is True but netbox-attachments is not installed")
        return None

    if Version(installed) < Version("11.0.0"):
        logger.error(
            "netbox-attachments %s is installed but >= 11.0.0 is required",
            installed,
        )
        return None

    try:
        from netbox_attachments.models import NetBoxAttachmentAssignment
    except ImportError:
        logger.error("Failed to import NetBoxAttachmentAssignment from netbox-attachments")
        return None

    return NetBoxAttachmentAssignment


def get_attachments_count_subquery(model_name: str):
    model = _get_attachment_model()
    if model is None:
        return Value(0)

    object_type = get_object_type_or_none("inventory_monitor", model_name)
    if not object_type:
        return Value(0)

    try:
        return Subquery(
            model.objects.filter(object_id=OuterRef("id"), object_type=object_type)
            .values("object_id")
            .annotate(attachments_count=Count("*"))
            .values("attachments_count")
        )
    except Exception:
        return Value(0)


@register.filter()
def format_price_with_currency(number, currency_code="EUR"):
    """Format number with currency symbol.

    Args:
        number (decimal): number to format
        currency_code (str): currency code (e.g., 'CZK', 'EUR', 'USD')

    Returns:
        str: Formatted number with currency symbol
    """
    if number is not None:
        res = number.to_integral() if number == number.to_integral() else number.normalize()
        formatted_number = f"{res:,}".replace(",", " ")
        currency_symbol = get_currency_symbol(currency_code) if currency_code else ""
        if currency_symbol:
            return f"{formatted_number} {currency_symbol}"
        else:
            return str(formatted_number)
    else:
        return "---"


class CurrencyColumn(django_tables2.Column):
    """Create a column that displays a price with currency symbol from the record.

    Args:
        tables (Column): Column class from django_tables2

    Returns:
        str: Formatted price with currency
    """

    def __init__(self, price_field="price", currency_field="currency", *args, **kwargs):
        self.price_field = price_field
        self.currency_field = currency_field
        super().__init__(*args, **kwargs)

    def render(self, value, record):
        price = getattr(record, self.price_field, None)
        currency = getattr(record, self.currency_field, None)
        return format_price_with_currency(price, currency)


TEMPLATE_SERVICES_END = """
{% for service in record.services.all %}
    {% if service.service_end %}
        <p>{{ service.service_end|date:"Y-m-d" }}</p>
    {% else %}
        <p>---</p>
    {% endif %}
{% endfor %}
"""

TEMPLATE_SERVICES_STATUS = (
    "{% load inventory_monitor %}"
    "{% for service in record.services.all %}"
    "{% with status=service|get_status:'service' %}"
    "{% if status %}"
    '<div class="progress mb-1" role="progressbar"'
    ' title=\'{{ service.service_start|date:"Y-m-d"|default:"?" }}'
    " — "
    '{{ service.service_end|date:"Y-m-d"|default:"∞" }}\'>'
    '<div class="progress-bar progress-bar-striped text-bg-{{ status.color }} w-100">'
    "{{ status.message }}</div></div>"
    "{% else %}"
    "{% if service.service_start or service.service_end %}"
    '<p title=\'{{ service.service_start|date:"Y-m-d"|default:"?" }}'
    " — "
    '{{ service.service_end|date:"Y-m-d"|default:"∞" }}\'>'
    '{{ service.service_start|date:"Y-m-d"|default:"?" }}'
    " — "
    '{{ service.service_end|date:"Y-m-d"|default:"∞" }}</p>'
    "{% endif %}"
    "{% endif %}"
    "{% endwith %}"
    "{% endfor %}"
)

TEMPLATE_SERVICES_START = """
{% for service in record.services.all %}
    {% if service.service_start %}
        <p>{{ service.service_start|date:"Y-m-d" }}</p>
    {% else %}
        <p>---</p>
    {% endif %}
{% endfor %}
"""

TEMPLATE_SERVICES_CONTRACTS = """
{% for service in record.services.all %}
    {% if service.contract %}
        <p>{{ service.contract.name }}</p>
    {% else %}
        <p>---</p>
    {% endif %}
{% endfor %}
"""


def make_status_template(status_type, start_field, end_field):
    """Generate a status progress bar template for a date range with tooltip."""
    return (
        "{{% load inventory_monitor %}}"
        "{{% with status=record|get_status:'{status_type}' %}}"
        "{{% if status %}}"
        '<div class="progress" role="progressbar"'
        ' title=\'{{{{ record.{start_field}|date:"Y-m-d"|default:"?" }}}}'
        " — "
        '{{{{ record.{end_field}|date:"Y-m-d"|default:"∞" }}}}\'>'
        '<div class="progress-bar progress-bar-striped text-bg-{{{{ status.color }}}} w-100">'
        "{{{{ status.message }}}}</div></div>"
        "{{% else %}}"
        "{{{{ ''|placeholder }}}}"
        "{{% endif %}}"
        "{{% endwith %}}"
    ).format(status_type=status_type, start_field=start_field, end_field=end_field)


TEMPLATE_INVOICING_STATUS = make_status_template("invoicing", "invoicing_start", "invoicing_end")
TEMPLATE_WARRANTY_STATUS = make_status_template("warranty", "warranty_start", "warranty_end")
