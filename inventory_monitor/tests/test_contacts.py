"""
Tests for the Contacts and Ownership features.

Both are opt-in NetBox capabilities the plugin's models inherit via mixins. Neither shows up in
`makemigrations` output for contacts, and the Contacts tab fails *silently* when its URL is not
registered, so these invariants are worth pinning explicitly.
"""

from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from netbox.models.features import get_model_features
from tenancy.models import Contact, ContactAssignment, ContactRole
from users.models import Owner

from inventory_monitor.filtersets import ExternalInventoryFilterSet
from inventory_monitor.models import (
    RMA,
    Asset,
    AssetService,
    AssetType,
    Contract,
    Contractor,
    ExternalInventory,
    Invoice,
    Probe,
)

# Models that opt into both ContactsMixin and OwnerMixin
SUPPORTED_MODELS = (
    Asset,
    AssetService,
    Contract,
    Contractor,
    ExternalInventory,
    Invoice,
    RMA,
)

# Deliberately excluded: AssetType is a lookup table, Probe is machine-generated telemetry
EXCLUDED_MODELS = (AssetType, Probe)


class ContactsFeatureTest(TestCase):
    """The feature registration and URL wiring that make the Contacts tab appear."""

    def test_supported_models_declare_contacts_feature(self):
        for model in SUPPORTED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertIn("contacts", get_model_features(model))

    def test_excluded_models_do_not_declare_contacts_feature(self):
        for model in EXCLUDED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertNotIn("contacts", get_model_features(model))

    def test_contacts_url_is_registered(self):
        """
        register_models() wires ObjectContactsView for every ContactsMixin subclass, but the tab
        renders only if the URL reverses. utilities/templatetags/tabs.py swallows NoReverseMatch,
        so dropping a get_model_urls() include from urls.py would remove the tab with no error
        raised anywhere -- this test is the only thing that would catch it.
        """
        for model in SUPPORTED_MODELS:
            with self.subTest(model=model.__name__):
                viewname = f"plugins:inventory_monitor:{model._meta.model_name}_contacts"
                try:
                    reverse(viewname, args=[1])
                except NoReverseMatch:
                    self.fail(f"{viewname} does not reverse; the Contacts tab would silently vanish")


class ContactAssignmentTest(TestCase):
    """Assigning a Contact to a plugin object, the way the ABRA importer does."""

    @classmethod
    def setUpTestData(cls):
        cls.role = ContactRole.objects.create(name="Owner", slug="owner")
        cls.contact = Contact.objects.create(name="Responsible Person")
        cls.item = ExternalInventory.objects.create(inventory_number="INV-0001", name="Item one")
        cls.other_item = ExternalInventory.objects.create(inventory_number="INV-0002", name="Item two")

    def test_assignment_passes_validation(self):
        """ContactAssignment.clean() rejects object types lacking the 'contacts' feature."""
        assignment = ContactAssignment(object=self.item, contact=self.contact, role=self.role)
        assignment.full_clean()
        assignment.save()

        self.assertEqual(self.item.get_contacts().count(), 1)
        self.assertEqual(self.other_item.get_contacts().count(), 0)

    def test_contact_filter_matches_only_assigned_objects(self):
        ContactAssignment.objects.create(object=self.item, contact=self.contact, role=self.role)

        filterset = ExternalInventoryFilterSet({"contact": [self.contact.pk]}, queryset=ExternalInventory.objects.all())
        self.assertEqual(list(filterset.qs), [self.item])

    def test_contact_role_filter_matches_only_assigned_objects(self):
        ContactAssignment.objects.create(object=self.item, contact=self.contact, role=self.role)

        filterset = ExternalInventoryFilterSet(
            {"contact_role": [self.role.pk]}, queryset=ExternalInventory.objects.all()
        )
        self.assertEqual(list(filterset.qs), [self.item])


class OwnershipTest(TestCase):
    """The owner ForeignKey added by netbox.models.mixins.OwnerMixin."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = Owner.objects.create(name="701 - Test department")
        cls.owned = ExternalInventory.objects.create(inventory_number="INV-0003", name="Owned item", owner=cls.owner)
        cls.unowned = ExternalInventory.objects.create(inventory_number="INV-0004", name="Unowned item")

    def test_supported_models_have_owner_field(self):
        for model in SUPPORTED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertIsNotNone(model._meta.get_field("owner"))

    def test_owner_is_optional(self):
        self.assertIsNone(self.unowned.owner)

    def test_owner_filter_matches_only_owned_objects(self):
        filterset = ExternalInventoryFilterSet({"owner_id": [self.owner.pk]}, queryset=ExternalInventory.objects.all())
        self.assertEqual(list(filterset.qs), [self.owned])
