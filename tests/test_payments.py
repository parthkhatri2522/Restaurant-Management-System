import unittest

from app import create_app
from app.extensions import db
from app.models import User, RestaurantOrder, Payment


class PaymentTests(unittest.TestCase):

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
                username="paymentcashier",
                email="paymentcashier@example.com",
                role="cashier",
                is_active=True
            )
            cashier.set_password("testpassword123")

            waiter = User(
                username="paymentwaiter",
                email="paymentwaiter@example.com",
                role="waiter",
                is_active=True
            )
            waiter.set_password("testpassword123")

            db.session.add_all([
                cashier,
                waiter
            ])

            order = RestaurantOrder(
                order_number="PAYMENT-TEST-001",
                customer_name="Payment Test Customer",
                order_type="dine_in",
                status="completed",
                subtotal=1000,
                tax_amount=0,
                discount_amount=0,
                total_amount=1000
            )

            db.session.add(order)
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

    def create_cash_payment(self, amount):
        return self.client.post(
            f"/api/payments/orders/{self.order_id}",
            json={
                "amount": amount,
                "payment_method": "cash"
            }
        )

    def test_create_cash_payment(self):
        self.login("paymentcashier")

        response = self.create_cash_payment(1000)

        self.assertEqual(response.status_code, 201)

        result = response.get_json()

        self.assertEqual(
            result["payment"]["payment_method"],
            "cash"
        )
        self.assertEqual(
            result["payment"]["status"],
            "completed"
        )
        self.assertEqual(
            result["payment_summary"]["outstanding_balance"],
            0.0
        )
        self.assertEqual(
            result["payment_summary"]["payment_status"],
            "paid"
        )

    def test_create_upi_payment_remains_pending(self):
        self.login("paymentcashier")

        response = self.client.post(
            f"/api/payments/orders/{self.order_id}",
            json={
                "amount": 500,
                "payment_method": "upi",
                "transaction_reference": "UPI-TEST-001"
            }
        )

        self.assertEqual(response.status_code, 201)

        result = response.get_json()

        self.assertEqual(
            result["payment"]["status"],
            "pending"
        )
        self.assertEqual(
            result["payment_summary"]["outstanding_balance"],
            1000.0
        )

    def test_multiple_partial_payments(self):
        self.login("paymentcashier")

        first_response = self.create_cash_payment(400)
        second_response = self.create_cash_payment(600)

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 201)

        result = second_response.get_json()

        self.assertEqual(
            result["payment_summary"]["net_paid"],
            1000.0
        )
        self.assertEqual(
            result["payment_summary"]["outstanding_balance"],
            0.0
        )
        self.assertEqual(
            result["payment_summary"]["payment_status"],
            "paid"
        )

    def test_overpayment_is_rejected(self):
        self.login("paymentcashier")

        response = self.create_cash_payment(1001)

        self.assertEqual(response.status_code, 400)

    def test_digital_payment_requires_reference(self):
        self.login("paymentcashier")

        response = self.client.post(
            f"/api/payments/orders/{self.order_id}",
            json={
                "amount": 500,
                "payment_method": "upi"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_pending_payment_can_be_completed_and_refunded(self):
        self.login("paymentcashier")

        create_response = self.client.post(
            f"/api/payments/orders/{self.order_id}",
            json={
                "amount": 500,
                "payment_method": "upi",
                "transaction_reference": "UPI-TEST-002"
            }
        )

        self.assertEqual(create_response.status_code, 201)

        payment_id = (
            create_response.get_json()["payment"]["id"]
        )

        complete_response = self.client.patch(
            f"/api/payments/{payment_id}/status",
            json={
                "status": "completed"
            }
        )

        self.assertEqual(complete_response.status_code, 200)

        self.assertEqual(
            complete_response.get_json()["payment"]["status"],
            "completed"
        )

        refund_response = self.client.patch(
            f"/api/payments/{payment_id}/status",
            json={
                "status": "refunded"
            }
        )

        self.assertEqual(refund_response.status_code, 200)

        result = refund_response.get_json()

        self.assertEqual(
            result["payment"]["status"],
            "refunded"
        )
        self.assertEqual(
            result["payment_summary"]["outstanding_balance"],
            1000.0
        )

    def test_duplicate_transaction_reference_is_rejected(self):
        self.login("paymentcashier")

        first_response = self.client.post(
            f"/api/payments/orders/{self.order_id}",
            json={
                "amount": 300,
                "payment_method": "upi",
                "transaction_reference": "DUPLICATE-REF-001"
            }
        )

        second_response = self.client.post(
            f"/api/payments/orders/{self.order_id}",
            json={
                "amount": 300,
                "payment_method": "upi",
                "transaction_reference": "DUPLICATE-REF-001"
            }
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 409)

    def test_waiter_cannot_record_payment(self):
        self.login("paymentwaiter")

        response = self.create_cash_payment(500)

        self.assertEqual(response.status_code, 403)

    def test_payment_history_can_be_retrieved(self):
        self.login("paymentcashier")

        self.create_cash_payment(400)

        response = self.client.get(
            f"/api/payments/orders/{self.order_id}"
        )

        self.assertEqual(response.status_code, 200)

        result = response.get_json()

        self.assertEqual(len(result["payments"]), 1)
        self.assertEqual(
            result["payment_summary"]["net_paid"],
            400.0
        )
        self.assertEqual(
            result["payment_summary"]["outstanding_balance"],
            600.0
        )


if __name__ == "__main__":
    unittest.main()