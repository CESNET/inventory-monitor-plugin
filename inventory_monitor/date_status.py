"""
Date status helpers for the Inventory Monitor plugin.

This module is deliberately free of model and template imports so it can be
shared by ``models.mixins``, ``templatetags.inventory_monitor`` and
``filtersets`` without creating import cycles.

Two related concepts live here:

* :func:`get_end_date_status` — the colour/message for a *single* end date
  (used by the coloured date badges in list tables).
* :class:`ServiceStatusChoices` / :class:`WarrantyStatusChoices` — the same
  bands expressed as filter choices.
"""

from django.utils import timezone
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


def get_end_date_status(end_date, attribute):
    """Return the colour and message for a bare end date.

    Unlike :meth:`DateStatusMixin.get_date_status` this looks at the end date
    only — there is no "Starts in X" branch, which would be misleading in a
    column that shows nothing but the end date.

    A missing end date is reported as open ended coverage. Whether that is
    meaningful depends on the caller: a service record without an end date is
    genuinely open ended, while a missing ``Asset.warranty_end`` just means the
    date was never recorded. The ``date_badge.html`` include decides via its
    ``open_ended`` flag.

    Args:
        end_date (datetime.date or None): The end date to evaluate.
        attribute (str): Warning threshold key ("service", "warranty", ...).

    Returns:
        dict or None: ``{"color": ..., "message": ...}``, or None when colour
        indicators are disabled for this attribute.
    """
    from inventory_monitor.settings import get_warning_days

    warning_days = get_warning_days(attribute)
    if warning_days is None:
        return None

    # Open ended — no end date means the coverage has not been bounded yet.
    if end_date is None:
        return {"color": "success", "message": "Active (no end date)"}

    days_until = (end_date - timezone.now().date()).days

    if days_until <= 0:
        return {
            "color": "danger",
            "message": f"Expired {format_time_delta(days_until)}",
        }
    if days_until <= warning_days:
        return {
            "color": "warning",
            "message": f"Expires {format_time_delta(days_until)}",
        }
    return {
        "color": "success",
        "message": f"Valid until {end_date.strftime('%Y-%m-%d')}",
    }
