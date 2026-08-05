from django.utils import timezone

from inventory_monitor.date_status import format_time_delta


class DateStatusMixin:
    """Mixin to provide date status functionality for models with start/end dates"""

    def get_date_status(self, start_field, end_field, status_type="", warning_days=None):
        """
        Returns the status and color for progress bar based on start and end dates.

        Memoized per instance: a list row renders the same status twice when both
        the status column and the end-date column are shown. The cache key
        includes the date values, so mutating a field invalidates it.

        Args:
            start_field (str): Name of the start date field
            end_field (str): Name of the end date field
            status_type (str): Type of status (e.g., "Warranty", "Service")
            warning_days (int or None): Number of days for the warning threshold.
                If None, no color indicators are shown (returns None).
        """
        if warning_days is None:
            return None

        start_date = getattr(self, start_field)
        end_date = getattr(self, end_field)

        cache = self.__dict__.setdefault("_date_status_cache", {})
        key = (start_field, end_field, warning_days, start_date, end_date)
        if key in cache:
            return cache[key]

        status = self._compute_date_status(start_date, end_date, warning_days)
        cache[key] = status
        return status

    @staticmethod
    def _compute_date_status(start_date, end_date, warning_days):
        today = timezone.now().date()

        def get_expiration_status(days_until):
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

        # No dates set
        if not start_date and not end_date:
            return None

        # Only end date set
        if not start_date and end_date:
            days_until = (end_date - today).days
            return get_expiration_status(days_until)

        # Future start
        if start_date and today < start_date:
            days_until = (start_date - today).days
            return {
                "color": "info",
                "message": f"Starts {format_time_delta(days_until)}",
            }

        # Both dates set
        if start_date and end_date:
            total_duration = (end_date - start_date).days
            days_until_expiration = (end_date - today).days

            # Simple logic for very short durations (2 days or less)
            if total_duration <= 2:
                if days_until_expiration <= 0:
                    return {
                        "color": "danger",
                        "message": f"Expired {format_time_delta(days_until_expiration)}",
                    }
                return {
                    "color": "warning",
                    "message": f"Expires {format_time_delta(days_until_expiration)}",
                }

            # Normal duration segment
            return get_expiration_status(days_until_expiration)

        # Active without end date
        return {
            "color": "success",
            "message": "Active",
        }
