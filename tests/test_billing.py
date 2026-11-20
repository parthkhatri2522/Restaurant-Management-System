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


class BillingTests(unittest.TestCase):

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
                username="testcashier",
                email="cashier@test.com",
                role="cashier",
                is_active=True
            )
            user.set_password("testpassword123")

            category = MenuCategory(name="Billing Test Category")

            db.session.add_all([user, category])
            db.session.flush()

            item = MenuItem(
                name="Test Burger",
                price=150.00,
                category_id=category.id,
                is_available=True
            )

            db.session.add(item)
            db.session.flush()

            order = RestaurantOrder(
                order_number="BILL-TEST-001",
                customer_name="Billing Test Customer",
                order_type="dine_in",
                status="served",
                subtotal=300.00,
                tax_amount=0,
                discount_amount=50.00,
                total_amount=250.00
            )

            db.session.add(order)
            db.session.flush()

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                quantity=2,
                unit_price=150.00,
                line_total=300.00
            )

            db.session.add(order_item)
            db.session.commit()

            self.order_id = order.id

        login_response = self.client.post(
            "/auth/login",
            json={
                "username": "testcashier",
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

    def test_get_order_bill(self):
        response = self.client.get(
            f"/api/billing/orders/{self.order_id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")

        bill = response.json["bill"]

        self.assertEqual(bill["order_number"], "BILL-TEST-001")
        self.assertEqual(bill["customer_name"], "Billing Test Customer")
        self.assertEqual(bill["subtotal"], 300.0)
        self.assertEqual(bill["discount_amount"], 50.0)
        self.assertEqual(bill["amount_payable"], 250.0)

    def test_bill_contains_item_details(self):
        response = self.client.get(
            f"/api/billing/orders/{self.order_id}"
        )

        self.assertEqual(response.status_code, 200)

        items = response.json["bill"]["items"]

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["item_name"], "Test Burger")
        self.assertEqual(items[0]["quantity"], 2)
        self.assertEqual(items[0]["line_total"], 300.0)

    def test_bill_for_nonexistent_order(self):
        response = self.client.get("/api/billing/orders/9999")

        self.assertEqual(response.status_code, 404)

    def test_unauthorized_role_cannot_access_billing(self):
        with self.app.app_context():
            user = User.query.filter_by(
                username="testcashier"
            ).first()

            user.role = "waiter"
            db.session.commit()

        response = self.client.get(
            f"/api/billing/orders/{self.order_id}"
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
