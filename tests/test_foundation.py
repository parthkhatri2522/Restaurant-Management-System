
import unittest

from app import create_app
from app.permissions import ROLES
from app.dashboards import DASHBOARD_CONFIG
from app.navigation import NAVIGATION_CONFIG


class ServeWiseFoundationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.testing = True

    def test_all_stakeholder_roles_exist(self):
        self.assertEqual(len(ROLES), 16)

    def test_dashboard_configuration_exists_for_all_roles(self):
        self.assertEqual(set(ROLES), set(DASHBOARD_CONFIG))

    def test_navigation_configuration_exists_for_all_roles(self):
        self.assertEqual(set(ROLES), set(NAVIGATION_CONFIG))

    def test_every_dashboard_has_required_fields(self):
        for role, dashboard in DASHBOARD_CONFIG.items():
            with self.subTest(role=role):
                self.assertIn("title", dashboard)
                self.assertIn("description", dashboard)
                self.assertIn("widgets", dashboard)
                self.assertIsInstance(dashboard["widgets"], list)

    def test_every_navigation_item_has_required_fields(self):
        required_fields = {
            "id", "label", "icon", "url", "permission"
        }

        for role, items in NAVIGATION_CONFIG.items():
            with self.subTest(role=role):
                self.assertIsInstance(items, list)

                for item in items:
                    self.assertTrue(
                        required_fields.issubset(item.keys())
                    )

    def test_dashboard_api_is_registered(self):
        routes = [
            rule.rule for rule in self.app.url_map.iter_rules()
        ]
        self.assertIn("/api/dashboard", routes)

    def test_navigation_api_is_registered(self):
        routes = [
            rule.rule for rule in self.app.url_map.iter_rules()
        ]
        self.assertIn("/api/navigation", routes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
