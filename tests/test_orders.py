
import unittest

from app import create_app
from app.extensions import db
from app.models import User, MenuCategory, MenuItem


class OrderTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite://",
            WTF_CSRF_ENABLED=False
        )

        self.context = self.app.app_context()
        self.context.push()

        db.create_all()

        self.client = self.app.test_client()

        self.user = User(
            username="order_test",
            email="order@test.com",
            role="waiter",
            is_active=True
        )
        self.user.set_password("TestPassword123")

        db.session.add(self.user)
        db.session.commit()

        self.category = MenuCategory(
            name="Test Category",
            description="Test category"
        )

        db.session.add(self.category)
        db.session.commit()

        self.menu_item = MenuItem(
            name="Test Pizza",
            description="Test menu item",
            price=200.00,
            category_id=self.category.id,
            is_available=True
        )

        db.session.add(self.menu_item)
        db.session.commit()

        self.client.post(
            "/auth/login",
            json={
                "username": "order_test",
                "password": "TestPassword123"
            }
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_create_order(self):
        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {
                        "menu_item_id": self.menu_item.id,
                        "quantity": 2
                    }
                ]
            }
        )

        self.assertEqual(response.status_code, 201)

        data = response.get_json()
        self.assertEqual(
            float(data["order"]["subtotal"]),
            400.00
        )

    def test_create_order_with_invalid_quantity(self):
        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {
                        "menu_item_id": self.menu_item.id,
                        "quantity": 0
                    }
                ]
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_create_order_with_unavailable_item(self):
        self.menu_item.is_available = False
        db.session.commit()

        response = self.client.post(
            "/api/orders",
            json={
                "items": [
                    {
                        "menu_item_id": self.menu_item.id,
                        "quantity": 1
                    }
                ]
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_get_orders(self):
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
