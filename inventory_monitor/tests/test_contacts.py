"""
Tests for the Contacts and Ownership features.

Both are opt-in NetBox capabilities the plugin's models inherit via `ContactsMixin` and
`PrimaryModel`. Several of the invariants here fail *silently* when broken, which is why they are
pinned explicitly:

- The Contacts tab disappears with no error if its URL stops reversing, because
  `utilities/templatetags/tabs.py` swallows `NoReverseMatch`.
- Listing `owner` in a form `FieldSet` renders the widget twice (the generic templates already
  render it), and on submit the second value silently overwrites the user's choice.
- `comments` on External Inventory and RMA used to be a form field with no backing column, so the
  text was discarded on save.
"""

import re

from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from netbox.models import PrimaryModel
from netbox.models.features import get_model_features
from tenancy.models import Contact, ContactAssignment, ContactRole
from users.models import Owner

from inventory_monitor import forms as im_forms
from inventory_monitor import filtersets as im_filtersets
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
from inventory_monitor.models.rma import RMAStatusChoices

# Models that inherit PrimaryModel + ContactsMixin
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

# Edit forms, which must render exactly one owner widget each
EDIT_FORMS = (
    "AssetForm",
    "AssetServiceForm",
    "ContractForm",
    "ContractorForm",
    "ExternalInventoryForm",
    "InvoiceForm",
    "RMAForm",
)

FILTERSETS = {
    Asset: im_filtersets.AssetFilterSet,
    AssetService: im_filtersets.AssetServiceFilterSet,
    Contract: im_filtersets.ContractFilterSet,
    Contractor: im_filtersets.ContractorFilterSet,
    ExternalInventory: im_filtersets.ExternalInventoryFilterSet,
    Invoice: im_filtersets.InvoiceFilterSet,
    RMA: im_filtersets.RMAFilterSet,
}


def build_instances(suffix):
    """Create one saved instance of every supported model, wired up with its required relations."""
    contractor = Contractor.objects.create(name=f"Contractor {suffix}")
    contract = Contract.objects.create(name=f"Contract {suffix}", name_internal=f"C-{suffix}", contractor=contractor)
    invoice = Invoice.objects.create(name=f"Invoice {suffix}", name_internal=f"I-{suffix}", contract=contract)
    asset = Asset.objects.create(serial=f"SN-{suffix}")
    service = AssetService.objects.create(asset=asset, contract=contract)
    rma = RMA.objects.create(asset=asset, issue_description="broken", status=RMAStatusChoices.PENDING)
    external = ExternalInventory.objects.create(inventory_number=f"INV-{suffix}", name=f"Item {suffix}")
    return {
        Asset: asset,
        AssetService: service,
        Contract: contract,
        Contractor: contractor,
        ExternalInventory: external,
        Invoice: invoice,
        RMA: rma,
    }


class ContactsFeatureTest(TestCase):
    """Feature registration and URL wiring — what makes the Contacts tab appear."""

    def test_supported_models_declare_contacts_feature(self):
        for model in SUPPORTED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertIn("contacts", get_model_features(model))

    def test_excluded_models_do_not_declare_contacts_feature(self):
        for model in EXCLUDED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertNotIn("contacts", get_model_features(model))

    def test_supported_models_inherit_primary_model(self):
        for model in SUPPORTED_MODELS:
            with self.subTest(model=model.__name__):
                self.assertTrue(issubclass(model, PrimaryModel))

    def test_contacts_url_is_registered(self):
        """
        register_models() wires ObjectContactsView for every ContactsMixin subclass, but the tab
        renders only if the URL reverses. tabs.py swallows NoReverseMatch, so dropping a
        get_model_urls() include from urls.py would remove the tab with no error raised anywhere.
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
        cls.matching = build_instances("A")
        cls.other = build_instances("B")
        for obj in cls.matching.values():
            ContactAssignment.objects.create(object=obj, contact=cls.contact, role=cls.role)

    def test_assignment_passes_validation(self):
        """ContactAssignment.clean() rejects object types lacking the 'contacts' feature."""
        extra = Contact.objects.create(name="Second Person")
        assignment = ContactAssignment(object=self.matching[Asset], contact=extra, role=self.role)
        assignment.full_clean()
        assignment.save()

        self.assertEqual(self.matching[Asset].get_contacts().count(), 2)
        self.assertEqual(self.other[Asset].get_contacts().count(), 0)

    def test_contact_filter_matches_only_assigned_objects(self):
        for model, filterset in FILTERSETS.items():
            with self.subTest(model=model.__name__):
                qs = filterset({"contact": [self.contact.pk]}, queryset=model.objects.all()).qs
                self.assertEqual(list(qs), [self.matching[model]])

    def test_contact_role_filter_matches_only_assigned_objects(self):
        for model, filterset in FILTERSETS.items():
            with self.subTest(model=model.__name__):
                qs = filterset({"contact_role": [self.role.pk]}, queryset=model.objects.all()).qs
                self.assertEqual(list(qs), [self.matching[model]])


class OwnershipTest(TestCase):
    """The owner ForeignKey inherited from PrimaryModel."""

    @classmethod
    def setUpTestData(cls):
        cls.owner = Owner.objects.create(name="701 - Test department")
        cls.owned = build_instances("A")
        cls.unowned = build_instances("B")
        for obj in cls.owned.values():
            obj.owner = cls.owner
            obj.save()

    def test_owner_is_optional(self):
        for model, obj in self.unowned.items():
            with self.subTest(model=model.__name__):
                self.assertIsNone(obj.owner)

    def test_owner_filter_matches_only_owned_objects(self):
        for model, filterset in FILTERSETS.items():
            with self.subTest(model=model.__name__):
                qs = filterset({"owner_id": [self.owner.pk]}, queryset=model.objects.all()).qs
                self.assertEqual(list(qs), [self.owned[model]])


class OwnerWidgetRenderingTest(TestCase):
    """
    Regression guard: `owner` and `owner_group` are rendered unconditionally by
    templates/htmx/form.html, so listing them in a FieldSet duplicates the widget and the second
    copy silently wins on POST.
    """

    def test_edit_forms_render_exactly_one_owner_widget(self):
        for form_name in EDIT_FORMS:
            with self.subTest(form=form_name):
                html = render_to_string("htmx/form.html", {"form": getattr(im_forms, form_name)()})
                self.assertEqual(len(re.findall(r'name="owner"', html)), 1)
                self.assertEqual(len(re.findall(r'name="owner_group"', html)), 1)


class DescriptionAndCommentsTest(TestCase):
    """External Inventory and RMA gained these columns in 14.0.0; the form input used to vanish."""

    def test_comments_persist(self):
        asset = Asset.objects.create(serial="SN-COMMENTS")
        cases = (
            ExternalInventory.objects.create(inventory_number="INV-C", name="Item"),
            RMA.objects.create(asset=asset, issue_description="broken", status=RMAStatusChoices.PENDING),
        )
        for obj in cases:
            with self.subTest(model=type(obj).__name__):
                obj.comments = "a comment that must survive a round trip"
                obj.description = "a description"
                obj.save()
                obj.refresh_from_db()
                self.assertEqual(obj.comments, "a comment that must survive a round trip")
                self.assertEqual(obj.description, "a description")
