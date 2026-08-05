"""
Date status bands for the Inventory Monitor plugin.

A date range falls into one of three bands — expired, expiring soon, valid —
decided by the ``warning_days`` threshold for its attribute. The band has to be
computed two ways: in Python for a single object (to colour a badge) and in SQL
for a whole queryset (to filter a list). :func:`date_status_q` is the SQL half
and :meth:`DateStatusMixin.get_date_status` is the Python half; the cut points
are documented together in :func:`date_status_q` so the two cannot drift.

This module imports no plugin models, so ``models.mixins`` can use it during
app loading without an import cycle. That is also why :func:`format_time_delta`
lives here rather than in ``helpers``, which pulls in ``core.models``.
"""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from utilities.choices import ChoiceSet


class DateStatusChoices(ChoiceSet):
    """Bands a date range can fall into, as filter choices."""

    EXPIRED = "expired"
    EXPIRING = "expiring"
    VALID = "valid"
    NONE = "none"

    CHOICES = [
        (EXPIRED, "Expired"),
        (EXPIRING, "Expiring soon"),
        (VALID, "Valid"),
        (NONE, "Not set"),
    ]


class ServiceStatusChoices(DateStatusChoices):
    """As above, but "not set" means the asset has no service records at all."""

    CHOICES = [
        (DateStatusChoices.EXPIRED, "Expired"),
        (DateStatusChoices.EXPIRING, "Expiring soon"),
        (DateStatusChoices.VALID, "Valid"),
        (DateStatusChoices.NONE, "No service records"),
    ]


def date_status_q(start_field, end_field, warning_days):
    """Return the ORM lookup for each band of a date range.

    This is the SQL mirror of DateStatusMixin._compute_date_status(), branch for
    branch. Keep the two in step: the badge colour and the filter band for the
    same record must agree.

        Python branch                         colour   SQL band
        no dates set                          (none)   none
        no start, end set                     by end   by end
        start in the future                   info     valid
        both set, started                     by end   by end
        start set, no end ("Active")          success  valid

    Cut points by end date, where days_until = (end_date - today).days:

        days_until <= 0             -> expired    end_date <= today
        days_until <= warning_days  -> expiring   today < end_date <= threshold
        otherwise                   -> valid      end_date > threshold

    Note the boundary: a period ending *today* is expired, not expiring.

    Args:
        start_field (str): Start-date field.
        end_field (str): End-date field.
        warning_days (int or None): Orange threshold. None (colour indicators
            disabled) collapses the expiring band to empty rather than folding
            it into valid, so the bands stay disjoint.

    Returns:
        dict: Band value -> Q object.
    """
    today = timezone.now().date()
    threshold = today + timedelta(days=warning_days or 0)

    # A NULL start counts as started. Spelled out rather than negating
    # "start > today", because SQL NOT(NULL > date) is NULL and drops the row.
    started = Q(**{f"{start_field}__isnull": True}) | Q(**{f"{start_field}__lte": today})
    not_started = Q(**{f"{start_field}__gt": today})
    open_ended = Q(**{f"{end_field}__isnull": True, f"{start_field}__isnull": False})

    return {
        DateStatusChoices.EXPIRED: started & Q(**{f"{end_field}__lte": today}),
        DateStatusChoices.EXPIRING: started & Q(**{f"{end_field}__gt": today, f"{end_field}__lte": threshold}),
        DateStatusChoices.VALID: (
            (started & Q(**{f"{end_field}__gt": threshold}))
            | (not_started & Q(**{f"{end_field}__isnull": False}))
            | open_ended
        ),
        DateStatusChoices.NONE: Q(**{f"{end_field}__isnull": True, f"{start_field}__isnull": True}),
    }


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
