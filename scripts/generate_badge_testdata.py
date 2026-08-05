"""
Generate Asset / AssetService records covering every Service End and
Warranty End badge state.

All records are prefixed with BADGE-TEST so they are easy to find and remove.

Create:
    /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell \
        < scripts/generate_badge_testdata.py

Remove (services first — AssetService.asset is on_delete=PROTECT):
    /opt/netbox/venv/bin/python /opt/netbox/netbox/manage.py shell \
        -c "from inventory_monitor.models import Asset, AssetService; \
            AssetService.objects.filter(asset__serial__startswith='BADGE-TEST').delete(); \
            Asset.objects.filter(serial__startswith='BADGE-TEST').delete()"
"""

from datetime import timedelta

from django.utils import timezone

from inventory_monitor.filtersets.asset import AssetFilterSet
from inventory_monitor.models import Asset, AssetService
from inventory_monitor.settings import get_warning_days

PREFIX = "BADGE-TEST"
today = timezone.now().date()
svc_days = get_warning_days("service")
war_days = get_warning_days("warranty")

print(f"today={today}  warning_days: service={svc_days} warranty={war_days}")

# Start clean so the script is safe to re-run. Services go first because
# AssetService.asset is on_delete=PROTECT.
AssetService.objects.filter(asset__serial__startswith=PREFIX).delete()
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


created = []


def case(serial, description, **kwargs):
    asset = make(serial, description, **kwargs)
    created.append(asset)
    svc = ", ".join(str(e) if e else "None" for _, e in kwargs.get("services", ())) or "-"
    print(f"  {asset.serial:28s} warranty_end={str(kwargs.get('warranty_end') or '-'):12s} service_end=[{svc}]")


# Boundaries of the orange band. today+N is the last orange day; today+N+1 is green.
if svc_days is None or war_days is None:
    raise SystemExit(
        "warning_days is disabled for service or warranty, so there are no band edges to "
        "generate. Set both keys to an integer before running this script."
    )

svc_edge_in, svc_edge_out = d(svc_days), d(svc_days + 1)
war_edge_in, war_edge_out = d(war_days), d(war_days + 1)

# --- Service End: one badge per state ---------------------------------------
case("SVC-RED", "Service expired long ago (red)", services=[(d(-800), d(-400))])
case("SVC-RED-EDGE", "Service ends today, counts as expired (red)", services=[(d(-400), d(0))])
case("SVC-ORANGE", "Service ends inside the warning window (orange)", services=[(d(-400), d(5))])
case("SVC-ORANGE-EDGE", "Service ends on the last orange day (orange)", services=[(d(-400), svc_edge_in)])
case("SVC-GREEN-EDGE", "Service ends one day past the window (green)", services=[(d(-400), svc_edge_out)])
case("SVC-GREEN", "Service ends far in the future (green)", services=[(d(-400), d(900))])
case("SVC-NULL", "Service with no end date, open ended (green infinity)", services=[(d(-100), None)])
case("SVC-FUTURE", "Service that has not started yet (blue)", services=[(d(30), d(500))])
case("SVC-NONE", "Asset with no service records at all (em dash)")

# --- Multiple services on one asset: one badge per line ----------------------
case(
    "SVC-MIXED",
    "Three services: red, orange and green on separate lines",
    services=[(d(-900), d(-500)), (d(-400), d(10)), (d(-200), d(700))],
)
case("SVC-MIXED-NULL", "Two services, one expired and one open ended", services=[(d(-900), d(-500)), (d(-100), None)])

# --- Warranty End: one badge per state --------------------------------------
case("WAR-RED", "Warranty expired long ago (red)", warranty_start=d(-800), warranty_end=d(-400))
case("WAR-RED-EDGE", "Warranty ends today, counts as expired (red)", warranty_start=d(-400), warranty_end=d(0))
case("WAR-ORANGE", "Warranty ends inside the warning window (orange)", warranty_start=d(-400), warranty_end=d(3))
case(
    "WAR-ORANGE-EDGE", "Warranty ends on the last orange day (orange)", warranty_start=d(-400), warranty_end=war_edge_in
)
case(
    "WAR-GREEN-EDGE", "Warranty ends one day past the window (green)", warranty_start=d(-400), warranty_end=war_edge_out
)
case("WAR-GREEN", "Warranty ends far in the future (green)", warranty_start=d(-400), warranty_end=d(900))
case("WAR-NULL", "Warranty start set but no end date (green infinity)", warranty_start=d(-100))
case("WAR-NONE", "No warranty dates at all (em dash)")

# --- Both columns populated, for filter cross-checks -------------------------
case(
    "BOTH-RED",
    "Service and warranty both expired",
    warranty_start=d(-800),
    warranty_end=d(-400),
    services=[(d(-800), d(-400))],
)
case(
    "BOTH-GREEN",
    "Service and warranty both valid",
    warranty_start=d(-400),
    warranty_end=d(900),
    services=[(d(-400), d(900))],
)
case(
    "BOTH-SPLIT",
    "Service expired but warranty still valid",
    warranty_start=d(-400),
    warranty_end=d(900),
    services=[(d(-800), d(-400))],
)

print()
print(f"created {len(created)} assets, {AssetService.objects.filter(asset__in=created).count()} services")
print()
print("View them at:")
print("  /plugins/inventory-monitor/assets/?q=BADGE-TEST")
print("Then use Configure Table to show Service Start, Service End and Warranty End.")
print()
print("Expected filter counts over the test data:")
base = Asset.objects.filter(serial__startswith=PREFIX)
for status in ("expired", "expiring", "valid", "none"):
    s = AssetFilterSet({"service_status": [status]}, queryset=base).qs.count()
    w = AssetFilterSet({"warranty_status": [status]}, queryset=base).qs.count()
    print(f"  {status:9s} service={s:2d}  warranty={w:2d}")
