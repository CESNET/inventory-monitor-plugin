"""
Generate Asset / AssetService records covering every Service End and
Warranty End badge state.

All records are prefixed with BADGE-TEST so they are easy to find and remove.

Create:
    /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell \
        < scripts/generate_badge_testdata.py

Remove:
    /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell \
        -c "from inventory_monitor.models import Asset; \
            Asset.objects.filter(serial__startswith='BADGE-TEST').delete()"
"""

from datetime import timedelta

from django.utils import timezone

from inventory_monitor.models import Asset, AssetService
from inventory_monitor.settings import get_warning_days

PREFIX = "BADGE-TEST"
today = timezone.now().date()
svc_days = get_warning_days("service")
war_days = get_warning_days("warranty")

print(f"today={today}  warning_days: service={svc_days} warranty={war_days}")

# Start clean so the script is safe to re-run.
deleted, _ = Asset.objects.filter(serial__startswith=PREFIX).delete()
if deleted:
    print(f"removed {deleted} objects from a previous run")


def d(days):
    """A date `days` from today (negative = past)."""
    return today + timedelta(days=days)


def make(serial, description, warranty_start=None, warranty_end=None, services=()):
    asset = Asset.objects.create(
        serial=f"{PREFIX}-{serial}",
        description=description,
        warranty_start=warranty_start,
        warranty_end=warranty_end,
    )
    for service_start, service_end in services:
        AssetService.objects.create(asset=asset, service_start=service_start, service_end=service_end)
    return asset


# Boundaries of the orange band. today+N is the last orange day; today+N+1 is green.
svc_edge_in = d(svc_days) if svc_days is not None else None
svc_edge_out = d(svc_days + 1) if svc_days is not None else None
war_edge_in = d(war_days) if war_days is not None else None
war_edge_out = d(war_days + 1) if war_days is not None else None

CASES = [
    # --- Service End: one badge per state -------------------------------
    ("SVC-RED", "Service expired long ago (red)", None, None, [(d(-800), d(-400))]),
    ("SVC-RED-EDGE", "Service ended today, counts as expired (red)", None, None, [(d(-400), d(0))]),
    ("SVC-ORANGE", "Service ends inside the warning window (orange)", None, None, [(d(-400), d(5))]),
    ("SVC-ORANGE-EDGE", "Service ends on the last orange day (orange)", None, None, [(d(-400), svc_edge_in)]),
    ("SVC-GREEN-EDGE", "Service ends one day past the window (green)", None, None, [(d(-400), svc_edge_out)]),
    ("SVC-GREEN", "Service ends far in the future (green)", None, None, [(d(-400), d(900))]),
    ("SVC-NULL", "Service with no end date, open ended (green infinity)", None, None, [(d(-100), None)]),
    ("SVC-FUTURE", "Service that has not started yet (green)", None, None, [(d(30), d(500))]),
    ("SVC-NONE", "Asset with no service records at all (em dash)", None, None, []),
    # --- Multiple services on one asset: one badge per line -------------
    (
        "SVC-MIXED",
        "Three services: red, orange and green on separate lines",
        None,
        None,
        [(d(-900), d(-500)), (d(-400), d(10)), (d(-200), d(700))],
    ),
    (
        "SVC-MIXED-NULL",
        "Two services, one expired and one open ended",
        None,
        None,
        [(d(-900), d(-500)), (d(-100), None)],
    ),
    # --- Warranty End: one badge per state ------------------------------
    ("WAR-RED", "Warranty expired long ago (red)", d(-800), d(-400), []),
    ("WAR-RED-EDGE", "Warranty ended today, counts as expired (red)", d(-400), d(0), []),
    ("WAR-ORANGE", "Warranty ends inside the warning window (orange)", d(-400), d(3), []),
    ("WAR-ORANGE-EDGE", "Warranty ends on the last orange day (orange)", d(-400), war_edge_in, []),
    ("WAR-GREEN-EDGE", "Warranty ends one day past the window (green)", d(-400), war_edge_out, []),
    ("WAR-GREEN", "Warranty ends far in the future (green)", d(-400), d(900), []),
    ("WAR-NULL", "Warranty start set but no end date (green infinity)", d(-100), None, []),
    ("WAR-NONE", "No warranty dates at all (em dash)", None, None, []),
    # --- Both columns populated, for filter cross-checks -----------------
    (
        "BOTH-RED",
        "Service and warranty both expired",
        d(-800),
        d(-400),
        [(d(-800), d(-400))],
    ),
    (
        "BOTH-GREEN",
        "Service and warranty both valid",
        d(-400),
        d(900),
        [(d(-400), d(900))],
    ),
    (
        "BOTH-SPLIT",
        "Service expired but warranty still valid",
        d(-400),
        d(900),
        [(d(-800), d(-400))],
    ),
]

created = []
for serial, description, w_start, w_end, services in CASES:
    asset = make(serial, description, w_start, w_end, services)
    created.append(asset)
    svc = ", ".join(str(e) if e else "None" for _, e in services) or "-"
    print(f"  {asset.serial:28s} warranty_end={str(w_end or '-'):12s} service_end=[{svc}]")

print()
print(f"created {len(created)} assets, {AssetService.objects.filter(asset__in=created).count()} services")
print()
print("View them at:")
print("  /plugins/inventory-monitor/assets/?q=BADGE-TEST")
print("Then use Configure Table to show Service Start, Service End and Warranty End.")
print()
print("Expected filter counts over the test data:")
for status in ("expired", "expiring", "valid", "none"):
    from inventory_monitor.filtersets.asset import AssetFilterSet

    base = Asset.objects.filter(serial__startswith=PREFIX)
    s = AssetFilterSet({"service_status": [status]}, queryset=base).qs.count()
    w = AssetFilterSet({"warranty_status": [status]}, queryset=base).qs.count()
    print(f"  {status:9s} service={s:2d}  warranty={w:2d}")
