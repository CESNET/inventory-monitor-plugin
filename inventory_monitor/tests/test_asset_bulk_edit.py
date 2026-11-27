"""Bulk Edit can assign several Assets to one dcim object at once, and clear the
assignment again (GitHub issue #14)."""

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from utilities.testing import TestCase, create_test_device

from inventory_monitor.models import Asset

URL = reverse("plugins:inventory_monitor:asset_bulk_edit")


class AssetBulkEditAssignmentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # See test_external_inventory_location: the content type cache holds ids of the live database
        ContentType.objects.clear_cache()
        cls.device = create_test_device("bulk-edit-device")
        cls.assets = [Asset.objects.create(serial=f"BULK-{i}") for i in range(2)]

    def setUp(self):
        super().setUp()
        self.add_permissions("inventory_monitor.view_asset", "inventory_monitor.change_asset")

    def _post(self, **data):
        response = self.client.post(URL, {"pk": [a.pk for a in self.assets], "_apply": True, **data})
        self.assertEqual(response.status_code, 302, getattr(response, "content", b"")[:2000])

    def test_assign_and_unassign(self):
        self._post(
            assigned_object_content_type=ContentType.objects.get_for_model(self.device).pk,
            assigned_object_object_id=self.device.pk,
        )
        for asset in Asset.objects.filter(pk__in=[a.pk for a in self.assets]):
            self.assertEqual(asset.assigned_object, self.device)

        self._post(_nullify=["assigned_object"])
        for asset in Asset.objects.filter(pk__in=[a.pk for a in self.assets]):
            self.assertIsNone(asset.assigned_object)

    def test_editing_another_field_keeps_the_assignment(self):
        Asset.objects.filter(pk__in=[a.pk for a in self.assets]).update(
            assigned_object_type=ContentType.objects.get_for_model(self.device), assigned_object_id=self.device.pk
        )
        self._post(project="bulk-project")
        for asset in Asset.objects.filter(pk__in=[a.pk for a in self.assets]):
            self.assertEqual(asset.project, "bulk-project")
            self.assertEqual(asset.assigned_object, self.device)

    def test_type_without_object_is_rejected(self):
        response = self.client.post(
            URL,
            {
                "pk": [a.pk for a in self.assets],
                "_apply": True,
                "assigned_object_content_type": ContentType.objects.get_for_model(self.device).pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Asset.objects.get(pk=self.assets[0].pk).assigned_object)
