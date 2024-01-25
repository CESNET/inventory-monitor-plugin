import django_tables2
from utilities.templatetags.builtins.filters import register
from django.contrib.contenttypes.models import ContentType


def get_content_type(app_label, model):
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model)
    except ProgrammingError:
        # Handle the case where the database schema has not yet been initialized
        content_type = ContentType.objects.none()


@register.filter()
def to_czech_crown(number):
    """Generate jinja2 filter to format number to czech crown.

    Args:
        number (decimal): number to format

    Returns:
        str: Formatted number
    """
    if number:
        res = (
            number.to_integral()
            if number == number.to_integral()
            else number.normalize()
        )
        return f"{res:,}".replace(",", " ") + " Kč"
    else:
        return "---"


class NumberColumn(django_tables2.Column):
    """Create a column that displays a number with a thousands separator.

    Args:
        tables (Column):  Column class from django_tables2

    Returns:
        str: Formatted number
    """

    def render(self, value):
        if value:
            res = (
                value.to_integral()
                if value == value.to_integral()
                else value.normalize()
            )
            return f"{res:,}".replace(",", " ") + " Kč"
        else:
            return "---"


TEMPLATE_SERVICES_END = """
{% for service in record.services.all %}
    {% if service.service_end %}
        <p>{{ service.service_end|date:"Y-n-d" }}</p>
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
