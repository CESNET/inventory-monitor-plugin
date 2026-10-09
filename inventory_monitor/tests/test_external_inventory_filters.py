"""The External Inventory status filter offers the codes present in the table,
labeled from ``external_inventory_status_config`` when configured and as the raw
code otherwise, and accepts several codes at once."""

from django.test import TestCase, override_settings

from inventory_monitor.filtersets.external_inventory import ExternalInventoryFilterSet
from inventory_monitor.forms.external_inventory import _distinct_choices, _status_label
from inventory_monitor.models import ExternalInventory

CONFIGURED = {"inventory_monitor": {"external_inventory_status_config": {"1": {"label": "Active", "color": "success"}}}}


status_choices = _distinct_choices("status", label=_status_label)


class ExternalInventoryStatusFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active = ExternalInventory.objects.create(inventory_number="INV-1", name="Active item", status="1")
        cls.unknown = ExternalInventory.objects.create(inventory_number="INV-9", name="Odd item", status="9")
        ExternalInventory.objects.create(inventory_number="INV-0", name="No status")

    @override_settings(PLUGINS_CONFIG=CONFIGURED)
    def test_choices_labeled_from_config(self):
        self.assertEqual(status_choices(), [("1", "Active (1)"), ("9", "9")])

    @override_settings(PLUGINS_CONFIG={"inventory_monitor": {}})
    def test_choices_without_config_are_raw_codes(self):
        self.assertEqual(status_choices(), [("1", "1"), ("9", "9")])

    @override_settings(PLUGINS_CONFIG={"inventory_monitor": {"external_inventory_status_config": None}})
    def test_choices_with_config_disabled_are_raw_codes(self):
        self.assertEqual(status_choices(), [("1", "1"), ("9", "9")])

    def test_filter_accepts_multiple_codes(self):
        qs = ExternalInventoryFilterSet({"status": ["1", "9"]}, ExternalInventory.objects.all()).qs
        self.assertCountEqual(qs, [self.active, self.unknown])
        qs = ExternalInventoryFilterSet({"status": ["1"]}, ExternalInventory.objects.all()).qs
        self.assertCountEqual(qs, [self.active])
