import unittest

from app import create_app
from app.extensions import db
from app.models import (
    User,
    MenuCategory,
    MenuItem,
    RestaurantOrder,
    OrderItem
)


class KitchenTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "WTF_CSRF_ENABLED": False
        })

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            user = User(
                username="testchef",
                email="chef@test.com",
                role="kitchen_staff",
                is_active=True
            )
            user.set_password("testpassword123")

            category = MenuCategory(name="Kitchen Test Category")

            db.session.add_all([user, category])
            db.session.flush()

            item = MenuItem(
                name="Test Pizza",
                price=200.00,
                category_id=category.id,
                is_available=True
            )

            db.session.add(item)
            db.session.flush()

            order = RestaurantOrder(
                order_number="KITCHEN-TEST-001",
                customer_name="Kitchen Test Customer",
                order_type="dine_in",
                status="confirmed",
                subtotal=200.00,
                tax_amount=0,
                discount_amount=0,
                total_amount=200.00
            )

            db.session.add(order)
            db.session.flush()

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                quantity=1,
                unit_price=200.00,
                line_total=200.00
            )

            db.session.add(order_item)
            db.session.commit()

            self.order_id = order.id

        login_response = self.client.post(
            "/auth/login",
            json={
                "username": "testchef",
                "password": "testpassword123"
            }
        )

        self.assertEqual(
            login_response.status_code,
            200,
            f"Login failed: {login_response.get_json()}"
        )

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_kitchen_orders(self):
        response = self.client.get("/api/kitchen/orders")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["count"], 1)

    def test_update_order_to_preparing(self):
        response = self.client.patch(
            f"/api/kitchen/orders/{self.order_id}/status",
            json={"status": "preparing"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["order"]["status"],
            "preparing"
        )

    def test_update_order_to_ready(self):
        with self.app.app_context():
            order = db.session.get(
                RestaurantOrder,
                self.order_id
            )
            order.status = "preparing"
            db.session.commit()

        response = self.client.patch(
            f"/api/kitchen/orders/{self.order_id}/status",
            json={"status": "ready"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json["order"]["status"],
            "ready"
        )

    def test_invalid_kitchen_status_transition(self):
        response = self.client.patch(
            f"/api/kitchen/orders/{self.order_id}/status",
            json={"status": "completed"}
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()