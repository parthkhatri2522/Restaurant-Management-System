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
from app.models.invoicing import (
    TaxConfiguration,
    RestaurantInvoice
)


class InvoiceTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://"
        })

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            cashier = User(
                username="testcashier",
                email="cashier@example.com",
                role="cashier",
                is_active=True
            )
            cashier.set_password("testpassword123")

            waiter = User(
                username="testwaiter",
                email="waiter@example.com",
                role="waiter",
                is_active=True
            )
            waiter.set_password("testpassword123")

            owner = User(
                username="testowner",
                email="owner@example.com",
                role="restaurant_owner",
                is_active=True
            )
            owner.set_password("testpassword123")

            db.session.add_all([
                cashier,
                waiter,
                owner
            ])

            category = MenuCategory(
                name="Main Course",
                description="Main course dishes"
            )
            db.session.add(category)
            db.session.flush()

            menu_item = MenuItem(
                category_id=category.id,
                name="Paneer Butter Masala",
                price=1000,
                is_available=True
            )
            db.session.add(menu_item)
            db.session.flush()

            order = RestaurantOrder(
                order_number="TEST-ORDER-001",
                customer_name="Test Customer",
                order_type="dine_in",
                status="completed",
                subtotal=1000,
                tax_amount=0,
                discount_amount=10,
                total_amount=990
            )
            db.session.add(order)
            db.session.flush()

            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=1,
                unit_price=1000,
                line_total=1000
            )
            db.session.add(order_item)

            config = TaxConfiguration(
                id=1,
                business_name="ServeWise Demo Restaurant",
                business_address="Demo Address",
                restaurant_state="Delhi",
                gst_rate=5,
                invoice_prefix="INV",
                is_gst_registered=False,
                is_demo=True
            )
            db.session.add(config)

            db.session.commit()

            self.order_id = order.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username, password="testpassword123"):
        return self.client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password
            }
        )

    def test_create_intrastate_invoice(self):
        self.login("testcashier")

        response = self.client.post(
            f"/api/invoices/orders/{self.order_id}",
            json={
                "place_of_supply_state": "Delhi"
            }
        )

        self.assertEqual(response.status_code, 201)

        invoice = response.get_json()["invoice"]

        self.assertEqual(invoice["tax_type"], "intra_state")
        self.assertEqual(invoice["taxable_value"], 990.0)
        self.assertEqual(invoice["cgst_amount"], 24.75)
        self.assertEqual(invoice["sgst_amount"], 24.75)
        self.assertEqual(invoice["igst_amount"], 0.0)
        self.assertEqual(invoice["total_tax"], 49.5)
        self.assertEqual(invoice["total_amount"], 1039.5)
        self.assertTrue(invoice["is_demo"])

    def test_create_interstate_invoice(self):
        self.login("testcashier")

        response = self.client.post(
            f"/api/invoices/orders/{self.order_id}",
            json={
                "place_of_supply_state": "Uttar Pradesh"
            }
        )

        self.assertEqual(response.status_code, 201)

        invoice = response.get_json()["invoice"]

        self.assertEqual(invoice["tax_type"], "inter_state")
        self.assertEqual(invoice["cgst_amount"], 0.0)
        self.assertEqual(invoice["sgst_amount"], 0.0)
        self.assertEqual(invoice["igst_amount"], 49.5)
        self.assertEqual(invoice["total_amount"], 1039.5)

    def test_duplicate_invoice_is_rejected(self):
        self.login("testcashier")

        first_response = self.client.post(
            f"/api/invoices/orders/{self.order_id}",
            json={
                "place_of_supply_state": "Delhi"
            }
        )

        second_response = self.client.post(
            f"/api/invoices/orders/{self.order_id}",
            json={
                "place_of_supply_state": "Delhi"
            }
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)

    def test_invalid_gstin_is_rejected(self):
        self.login("testowner")

        response = self.client.put(
            "/api/gst/configuration",
            json={
                "gstin": "INVALID-GSTIN"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_waiter_cannot_create_invoice(self):
        self.login("testwaiter")

        response = self.client.post(
            f"/api/invoices/orders/{self.order_id}",
            json={
                "place_of_supply_state": "Delhi"
            }
        )

        self.assertEqual(response.status_code, 403)

    def test_invoice_can_be_retrieved(self):
        self.login("testcashier")

        create_response = self.client.post(
            f"/api/invoices/orders/{self.order_id}",
            json={
                "place_of_supply_state": "Delhi"
            }
        )

        self.assertEqual(create_response.status_code, 201)

        invoice_id = create_response.get_json()["invoice"]["id"]

        response = self.client.get(
            f"/api/invoices/{invoice_id}"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["invoice"]["id"],
            invoice_id
        )


if __name__ == "__main__":
    unittest.main()