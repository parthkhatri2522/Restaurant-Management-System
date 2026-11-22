from datetime import datetime, timedelta

import pytest

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
        SECRET_KEY="reservation-enhancement-test"
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
            username="reservation_enhancement_owner",
            email="reservation_enhancement_owner@example.com",
            role="restaurant_owner",
            is_active=True
        )
        user.set_password("TestPassword123")
        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/auth/login",
        json={
            "username": "reservation_enhancement_owner",
            "password": "TestPassword123"
        }
    )
    assert response.status_code == 200
    return True


class TestReservationEnhancements:

    def test_reservation_page_contains_calendar(self, client, owner):
        response = client.get("/reservations")
        assert response.status_code == 200
        assert b"calendar-view" in response.data
        assert b"calendar-days" in response.data

    def test_reservation_page_contains_quick_filters(self, client, owner):
        response = client.get("/reservations")
        assert response.status_code == 200
        assert b'data-period="today"' in response.data
        assert b'data-period="upcoming"' in response.data
        assert b'data-period="past"' in response.data

    def test_reservation_page_contains_export_button(self, client, owner):
        response = client.get("/reservations")
        assert response.status_code == 200
        assert b"export-reservations" in response.data
        assert b"Export CSV" in response.data

    def test_reservation_page_contains_list_and_calendar_views(self, client, owner):
        response = client.get("/reservations")
        assert response.status_code == 200
        assert b'data-view="calendar"' in response.data
        assert b'data-view="list"' in response.data

    def test_reservation_enhancement_javascript_is_available(self, client):
        response = client.get("/static/js/reservations.js")
        assert response.status_code == 200
        assert b"function renderCalendar" in response.data
        assert b"function exportCSV" in response.data
        assert b"function setPeriod" in response.data

    def test_reservation_enhancement_stylesheet_is_available(self, client):
        response = client.get("/static/css/reservations.css")
        assert response.status_code == 200
        assert b".calendar-grid" in response.data
        assert b".day-reservation-card" in response.data

    def test_reservation_api_still_works(self, client, owner):
        response = client.get("/api/reservations")
        assert response.status_code == 200

    def test_reservation_page_requires_login(self, client):
        response = client.get("/reservations")
        assert response.status_code in (302, 401)