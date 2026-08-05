"""The Service/Warranty Status filters must select exactly the records whose
badge carries the matching colour.

Two implementations decide the same thing: DateStatusMixin._compute_date_status
in Python (which colours the badge) and date_status_q in SQL (which drives the
filter). They are easy to drift apart, and have — a period ending *today*, one
that has not started yet, and an open-ended one all used to land in a different
band than their colour suggested.

Ground truth here is the badge colour, never a date boundary restated in the
test. A test that recomputes the cut points proves only that the test agrees
with itself; that is how the original bugs survived review.
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from inventory_monitor.date_status import DateStatusChoices
from inventory_monitor.filtersets.asset import AssetFilterSet
from inventory_monitor.models import Asset, AssetService
from inventory_monitor.settings import get_warning_days

# A blue "starts in N days" badge is not expired and not expiring, so the
# filter groups it with valid. This is the only colour that is not its own band.
COLOUR_TO_BAND = {
    "danger": DateStatusChoices.EXPIRED,
    "warning": DateStatusChoices.EXPIRING,
    "success": DateStatusChoices.VALID,
    "info": DateStatusChoices.VALID,
}


class DateStatusBandTest(TestCase):
    """Every filter band must equal the set of assets badged with its colour."""

    @classmethod
    def setUpTestData(cls):
        today = timezone.now().date()
        svc = get_warning_days("service")
        war = get_warning_days("warranty")

        def d(days):
            return today + timedelta(days=days)

        def asset(serial, warranty_start=None, warranty_end=None, services=()):
            obj = Asset.objects.create(serial=serial, warranty_start=warranty_start, warranty_end=warranty_end)
            for start, end in services:
                AssetService.objects.create(asset=obj, service_start=start, service_end=end)
            return obj

        # One asset per badge state, including the band edges and every case
        # that has previously drifted between colour and filter.
        asset("EXPIRED", warranty_start=d(-800), warranty_end=d(-400), services=[(d(-800), d(-400))])
        asset("ENDS-TODAY", warranty_start=d(-400), warranty_end=d(0), services=[(d(-400), d(0))])
        asset("LAST-ORANGE-DAY", warranty_start=d(-400), warranty_end=d(war), services=[(d(-400), d(svc))])
        asset("FIRST-GREEN-DAY", warranty_start=d(-400), warranty_end=d(war + 1), services=[(d(-400), d(svc + 1))])
        asset("VALID", warranty_start=d(-400), warranty_end=d(900), services=[(d(-400), d(900))])
        asset("OPEN-ENDED", warranty_start=d(-100), services=[(d(-100), None)])
        asset("NOT-STARTED", warranty_start=d(30), warranty_end=d(500), services=[(d(30), d(500))])
        # Starts soon AND ends inside the warning window: blue, not orange.
        asset("NOT-STARTED-ENDS-SOON", warranty_start=d(10), warranty_end=d(40), services=[(d(10), d(40))])
        asset("END-ONLY", warranty_end=d(-5), services=[(None, d(-5))])
        asset("NO-DATES", services=[(None, None)])
        asset("NOTHING")
        asset(
            "MIXED",
            warranty_start=d(-400),
            warranty_end=d(900),
            services=[(d(-900), d(-500)), (d(-400), d(5)), (d(-200), d(700))],
        )

    def _expected_bands(self):
        """Derive the expected membership of each band from the badge colours."""
        service = {band: set() for band in DateStatusChoices.values()}
        warranty = {band: set() for band in DateStatusChoices.values()}

        for asset in Asset.objects.prefetch_related("services"):
            services = list(asset.services.all())
            if not services:
                # For an asset, "none" means no service records at all.
                service[DateStatusChoices.NONE].add(asset.pk)
            for record in services:
                status = record.get_service_status()
                if status:
                    service[COLOUR_TO_BAND[status["color"]]].add(asset.pk)

            status = asset.get_warranty_status()
            if status:
                warranty[COLOUR_TO_BAND[status["color"]]].add(asset.pk)
            else:
                warranty[DateStatusChoices.NONE].add(asset.pk)

        return {"service": service, "warranty": warranty}

    def test_filter_bands_match_badge_colours(self):
        for attribute, expected in self._expected_bands().items():
            for band, want in expected.items():
                with self.subTest(attribute=attribute, band=band):
                    got = set(
                        AssetFilterSet({f"{attribute}_status": [band]}, queryset=Asset.objects.all()).qs.values_list(
                            "pk", flat=True
                        )
                    )
                    self.assertEqual(
                        got,
                        want,
                        f"{attribute}_status={band} does not match the assets badged with that colour. "
                        f"Only in filter: {self._serials(got - want)}. "
                        f"Only in badges: {self._serials(want - got)}.",
                    )

    @staticmethod
    def _serials(pks):
        return sorted(Asset.objects.filter(pk__in=pks).values_list("serial", flat=True))
