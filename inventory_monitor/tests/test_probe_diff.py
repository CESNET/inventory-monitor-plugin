"""The Probe Diff page requires the view permission on Probe and rejects bad
input through the form instead of raising."""

from django.urls import reverse
from utilities.testing import TestCase, create_test_device

URL = reverse("plugins:inventory_monitor:probediff")


class ProbeDiffViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.device = create_test_device("probe-diff-device")

    def test_requires_view_probe_permission(self):
        self.assertEqual(self.client.get(URL).status_code, 403)
        self.assertEqual(self.client.post(URL, {"device": self.device.pk}).status_code, 403)

    def test_renders_with_permission(self):
        self.add_permissions("inventory_monitor.view_probe")
        self.assertEqual(self.client.get(URL).status_code, 200)
        response = self.client.post(URL, {"device": self.device.pk, "date_from": "2026-01-01", "date_to": "2026-02-01"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("probes_added", response.context)

    def test_invalid_dates_show_form_errors(self):
        self.add_permissions("inventory_monitor.view_probe")
        response = self.client.post(URL, {"device": self.device.pk, "date_from": "not-a-date", "date_to": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertNotIn("probes_added", response.context)
