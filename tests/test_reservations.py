
import unittest

from app import create_app
from app.extensions import db
from app.models import User, RestaurantTable, Reservation


class ReservationTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite://",
            WTF_CSRF_ENABLED=False
        )

        self.client = self.app.test_client()

        self.context = self.app.app_context()
        self.context.push()

        db.create_all()

        self.user = User(
            username="reservation_test",
            email="reservation@test.com",
            role="host",
            is_active=True
        )
        self.user.set_password("TestPassword123")

        db.session.add(self.user)
        db.session.commit()

        self.table = RestaurantTable(
            table_number="T101",
            capacity=4,
            status="available",
            is_active=True
        )

        db.session.add(self.table)
        db.session.commit()

        self.client.post(
            "/auth/login",
            json={
                "username": "reservation_test",
                "password": "TestPassword123"
            }
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_reservation_list_endpoint(self):
        response = self.client.get("/api/reservations")
        self.assertEqual(response.status_code, 200)

    def test_create_reservation(self):
        response = self.client.post(
            "/api/reservations",
            json={
                "customer_name": "Test Customer",
                "customer_phone": "9876543210",
                "reservation_time": "2026-12-20T19:00:00",
                "party_size": 3,
                "table_id": self.table.id
            }
        )

        self.assertEqual(response.status_code, 201)

    def test_invalid_party_size(self):
        response = self.client.post(
            "/api/reservations",
            json={
                "customer_name": "Test Customer",
                "customer_phone": "9876543210",
                "reservation_time": "2026-12-20T19:00:00",
                "party_size": 0
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_nonexistent_reservation(self):
        response = self.client.get("/api/reservations/9999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
