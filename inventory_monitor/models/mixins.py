from django.utils import timezone


class DateStatusMixin:
    """Mixin to provide date status functionality for models with start/end dates"""

    def get_date_status(self, start_field, end_field, status_type="", warning_days=None):
        """
        Returns the status and color for progress bar based on start and end dates.

        Args:
            start_field (str): Name of the start date field
            end_field (str): Name of the end date field
            status_type (str): Type of status (e.g., "Warranty", "Service")
            warning_days (int or None): Number of days for the warning threshold.
                If None, no color indicators are shown (returns None).
        """
        if warning_days is None:
            return None

        today = timezone.now().date()
        start_date = getattr(self, start_field)
        end_date = getattr(self, end_field)

        def format_time_delta(days):
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
