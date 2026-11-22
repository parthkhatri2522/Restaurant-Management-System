import pytest

from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    test_app = create_app()

    test_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key"
    )

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def owner(app, client):
    with app.app_context():
        user = User(
            username="reservation_owner",
            email="reservation_owner@example.com",
            role="restaurant_owner",
            is_active=True
        )

        user.set_password("TestPassword123")

        db.session.add(user)
        db.session.commit()

        user_id = user.id

    client.post(
        "/auth/login",
        json={
            "username": "reservation_owner",
            "password": "TestPassword123"
        }
    )

    return user_id


def reservation_payload(**overrides):
    payload = {
        "customer_name": "Test Customer",
        "customer_phone": "9876543210",
        "reservation_time": (
            datetime.now() + timedelta(days=1)
        ).replace(microsecond=0).isoformat(),
        "party_size": 4
    }

    payload.update(overrides)
    return payload


class TestReservationInterface:

    def test_reservations_page_requires_login(self, client):
        response = client.get("/reservations")

        assert response.status_code in (302, 401)

    def test_reservations_page_loads_for_owner(self, client, owner):
        response = client.get("/reservations")

        assert response.status_code == 200
        assert b"Reservation Management" in response.data
        assert b"Add Reservation" in response.data

    def test_reservations_css_is_available(self, client, owner):
        response = client.get("/static/css/reservations.css")

        assert response.status_code == 200
        assert b".reservation-stats" in response.data

    def test_reservations_javascript_is_available(self, client, owner):
        response = client.get("/static/js/reservations.js")

        assert response.status_code == 200
        assert b"loadReservations" in response.data

    def test_reservation_page_contains_filters(self, client, owner):
        response = client.get("/reservations")

        assert b"reservation-search" in response.data
        assert b"status-filter" in response.data
        assert b"date-filter" in response.data

    def test_owner_can_view_empty_reservation_list(self, client, owner):
        response = client.get("/api/reservations")

        assert response.status_code == 200
        assert response.get_json() == []

    def test_owner_can_create_reservation(self, client, owner):
        response = client.post(
            "/api/reservations",
            json=reservation_payload()
        )

        assert response.status_code == 201

        reservation = response.get_json()["reservation"]

        assert reservation["customer_name"] == "Test Customer"
        assert reservation["customer_phone"] == "9876543210"
        assert reservation["party_size"] == 4
        assert reservation["status"] == "pending"

    def test_owner_can_update_reservation(self, client, owner):
        create_response = client.post(
            "/api/reservations",
            json=reservation_payload()
        )

        reservation_id = create_response.get_json()["reservation"]["id"]

        update_response = client.put(
            f"/api/reservations/{reservation_id}",
            json={
                "customer_name": "Updated Customer",
                "customer_phone": "9999999999",
                "party_size": 6
            }
        )

        assert update_response.status_code == 200

        updated = update_response.get_json()["reservation"]

        assert updated["customer_name"] == "Updated Customer"
        assert updated["customer_phone"] == "9999999999"
        assert updated["party_size"] == 6

    def test_owner_can_change_reservation_status(self, client, owner):
        create_response = client.post(
            "/api/reservations",
            json=reservation_payload()
        )

        reservation_id = create_response.get_json()["reservation"]["id"]

        status_response = client.patch(
            f"/api/reservations/{reservation_id}/status",
            json={"status": "confirmed"}
        )

        assert status_response.status_code == 200
        assert (
            status_response.get_json()["reservation"]["status"]
            == "confirmed"
        )

    def test_invalid_reservation_status_is_rejected(self, client, owner):
        create_response = client.post(
            "/api/reservations",
            json=reservation_payload()
        )

        reservation_id = create_response.get_json()["reservation"]["id"]

        response = client.patch(
            f"/api/reservations/{reservation_id}/status",
            json={"status": "seated"}
        )

        assert response.status_code == 400

    def test_missing_required_fields_are_rejected(self, client, owner):
        response = client.post(
            "/api/reservations",
            json={
                "customer_name": "Test Customer"
            }
        )

        assert response.status_code == 400

    def test_invalid_party_size_is_rejected(self, client, owner):
        response = client.post(
            "/api/reservations",
            json=reservation_payload(party_size=0)
        )

        assert response.status_code == 400

    def test_nonexistent_reservation_returns_404(self, client, owner):
        response = client.get("/api/reservations/99999")

        assert response.status_code == 404

    def test_invalid_date_filter_is_rejected(self, client, owner):
        response = client.get("/api/reservations?date=invalid-date")

        assert response.status_code == 400

    def test_invalid_status_filter_is_rejected(self, client, owner):
        response = client.get("/api/reservations?status=seated")

        assert response.status_code == 400