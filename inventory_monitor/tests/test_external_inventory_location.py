"""External Inventory items can be placed on a dcim Region, Site or Location
(`location_assigned_object`). The hierarchical filters and the dcim tabs must agree:
an item on a Location shows up under its Site and under the Site's Region."""

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from dcim.models import Location, Region, Site

from inventory_monitor.filtersets.external_inventory import ExternalInventoryFilterSet
from inventory_monitor.forms.external_inventory import ExternalInventoryBulkImportForm, ExternalInventoryForm
from inventory_monitor.helpers import location_assignment_q
from inventory_monitor.models import ExternalInventory
from inventory_monitor.template_content import LocationExternalInventoryView


def _filter(**params):
    return ExternalInventoryFilterSet(params, ExternalInventory.objects.all()).qs


class ExternalInventoryLocationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # `manage.py test` runs system checks against the live database first, which fills the
        # content type cache with ids that do not exist in the freshly created test database.
        ContentType.objects.clear_cache()
        cls.europe = Region.objects.create(name="Europe", slug="europe")
        cls.czechia = Region.objects.create(name="Czechia", slug="czechia", parent=cls.europe)
        cls.other_region = Region.objects.create(name="Elsewhere", slug="elsewhere")
        cls.site = Site.objects.create(name="Praha", slug="praha", region=cls.czechia)
        cls.other_site = Site.objects.create(name="Brno", slug="brno", region=cls.other_region)
        cls.floor = Location.objects.create(name="Floor 5", slug="floor-5", site=cls.site)
        cls.room = Location.objects.create(name="Room B5.34", slug="room-b5-34", site=cls.site, parent=cls.floor)

        cls.on_region = ExternalInventory.objects.create(
            inventory_number="R1", name="On region", location_assigned_object=cls.czechia
        )
        cls.on_site = ExternalInventory.objects.create(
            inventory_number="S1", name="On site", location_assigned_object=cls.site
        )
        cls.on_room = ExternalInventory.objects.create(
            inventory_number="L1", name="On room", location_assigned_object=cls.room, external_location_id="EXT-ROOM"
        )
        cls.elsewhere = ExternalInventory.objects.create(
            inventory_number="X1", name="Elsewhere", location_assigned_object=cls.other_site
        )
        cls.unplaced = ExternalInventory.objects.create(inventory_number="U1", name="Unplaced")

    def test_generic_fk_round_trip(self):
        item = ExternalInventory.objects.get(pk=self.on_room.pk)
        self.assertEqual(item.location_assigned_object, self.room)
        self.assertEqual(item.location_assigned_object_type.model, "location")

    def test_exact_filters(self):
        qs = _filter(location_assigned_object_type="dcim.site", location_assigned_object_id=[self.site.pk])
        self.assertCountEqual(qs, [self.on_site])

    def test_external_location_id_filter(self):
        # `q=` is not asserted: instances that wrap search in UNACCENT() cannot run it on a test database
        self.assertCountEqual(_filter(external_location_id=["EXT-ROOM"]), [self.on_room])

    def test_site_filter_includes_its_locations(self):
        self.assertCountEqual(_filter(site_id=[self.site.pk]), [self.on_site, self.on_room])

    def test_location_filter_includes_descendants(self):
        self.assertCountEqual(_filter(location_id=[self.floor.pk]), [self.on_room])
        self.assertCountEqual(_filter(location_id=[self.room.pk]), [self.on_room])

    def test_region_filter_rolls_up_subregions_sites_and_locations(self):
        self.assertCountEqual(_filter(region_id=[self.europe.pk]), [self.on_region, self.on_site, self.on_room])
        self.assertCountEqual(_filter(region_id=[self.other_region.pk]), [self.elsewhere])

    def test_unknown_model_matches_nothing(self):
        self.assertFalse(ExternalInventory.objects.filter(location_assignment_q(ExternalInventory, [1])).exists())

    def test_tabs_use_the_same_scope_as_the_filters(self):
        self.assertCountEqual(LocationExternalInventoryView.items_for(self.site), [self.on_site, self.on_room])
        self.assertCountEqual(
            LocationExternalInventoryView.items_for(self.europe), [self.on_region, self.on_site, self.on_room]
        )
        self.assertCountEqual(LocationExternalInventoryView.items_for(self.floor), [self.on_room])

    def test_tab_urls_reverse(self):
        # tabs.py swallows NoReverseMatch, so a broken registration would hide the tab silently
        for name, obj in (
            ("dcim:region_external_inventory", self.europe),
            ("dcim:site_external_inventory", self.site),
            ("dcim:location_external_inventory", self.room),
        ):
            self.assertTrue(reverse(name, args=[obj.pk]))

    def test_form_rejects_two_targets_and_sets_one(self):
        base = {"inventory_number": "F1", "name": "Form item"}
        form = ExternalInventoryForm(data={**base, "assigned_site": self.site.pk, "assigned_location": self.room.pk})
        self.assertFalse(form.is_valid())
        self.assertIn("single Region, Site or Location", str(form.errors))

        form = ExternalInventoryForm(data={**base, "assigned_site": self.site.pk})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().location_assigned_object, self.site)

        form = ExternalInventoryForm(instance=self.on_room)
        self.assertEqual(form.initial["assigned_location"], self.room)

    def test_import_form_sets_target(self):
        form = ExternalInventoryBulkImportForm(
            data={"inventory_number": "I1", "name": "Imported", "assigned_region_id": self.czechia.pk}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().location_assigned_object, self.czechia)
