"""
Date status helpers for the Inventory Monitor plugin.

This module is deliberately free of model and template imports so it can be
shared by ``models.mixins`` and ``filtersets`` without creating import cycles.

Colour and message for a date range are produced by a single function,
:meth:`DateStatusMixin.get_date_status`. The status bars and the date badges
both read it through the ``get_status`` template filter, so they cannot
disagree. What lives here is the surrounding vocabulary: the default warning
thresholds, the relative time formatter, and the same colour bands expressed
as filter choices.
"""

from utilities.choices import ChoiceSet

# Warning thresholds applied when ``warning_days`` does not mention an
# attribute at all. Setting the key explicitly to ``None`` disables colour
# indicators for that attribute — see ``settings.get_warning_days``.
DEFAULT_WARNING_DAYS = {
    "service": 60,
    "warranty": 60,
    "invoicing": 30,
}


class DateStatusChoices:
    """Status band values shared by the Service and Warranty status filters.

    Deliberately not a ChoiceSet — NetBox's ChoiceSet metaclass requires a
    CHOICES attribute on every class, so the shared constants live here and
    the two concrete ChoiceSets below supply their own labels.
    """

    EXPIRED = "expired"
    EXPIRING = "expiring"
    VALID = "valid"
    NONE = "none"


class ServiceStatusChoices(ChoiceSet):
    CHOICES = [
        (DateStatusChoices.EXPIRED, "Expired", "red"),
        (DateStatusChoices.EXPIRING, "Expiring soon", "orange"),
        (DateStatusChoices.VALID, "Valid", "green"),
        (DateStatusChoices.NONE, "No service records", "gray"),
    ]


class WarrantyStatusChoices(ChoiceSet):
    CHOICES = [
        (DateStatusChoices.EXPIRED, "Expired", "red"),
        (DateStatusChoices.EXPIRING, "Expiring soon", "orange"),
        (DateStatusChoices.VALID, "Valid", "green"),
        (DateStatusChoices.NONE, "Not set", "gray"),
    ]


def format_time_delta(days):
    """Render a signed day count as a human readable relative time.

    Args:
        days (int): Days until the date; negative values are in the past.

    Returns:
        str: e.g. "in 45 days", "3 months ago", "in 2 years", "today"
    """
    if days == 0:
        return "today"
    is_past = days < 0
    days = abs(days)
    if days < 90:
        unit = "day" if days == 1 else "days"
        value = f"{days} {unit}"
    elif days < 730:
        months = round(days / 30.44)
        unit = "month" if months == 1 else "months"
        value = f"{months} {unit}"
    else:
        years = round(days / 365.25)
        unit = "year" if years == 1 else "years"
        value = f"{years} {unit}"
    return f"{value} ago" if is_past else f"in {value}"
