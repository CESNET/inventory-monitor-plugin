"""Every plugin menu link must reverse. The menu renders on every NetBox page
for users who hold the permission, so a dangling link name is a site-wide 500
that permission-scoped view tests never see."""

from django.test import SimpleTestCase
from django.urls import reverse

from inventory_monitor.navigation import menu


class MenuLinksTest(SimpleTestCase):
    def test_all_menu_links_reverse(self):
        for group in menu.groups:
            for item in group.items:
                with self.subTest(link=item.link):
                    reverse(item.link)
                for button in item.buttons:
                    with self.subTest(link=button.link):
                        reverse(button.link)
