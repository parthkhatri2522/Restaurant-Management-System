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
            username="table_owner",
            email="table_owner@example.com",
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
            "username": "table_owner",
            "password": "TestPassword123"
        }
    )

    return user_id


class TestTableInterface:

    def test_tables_page_requires_login(self, client):
        response = client.get("/tables")

        assert response.status_code in (302, 401)

    def test_tables_page_loads_for_owner(self, client, owner):
        response = client.get("/tables")

        assert response.status_code == 200
        assert b"Table Management" in response.data
        assert b"Add New Table" in response.data

    def test_tables_css_is_available(self, client, owner):
        response = client.get("/static/css/tables.css")

        assert response.status_code == 200
        assert b".table-card" in response.data

    def test_tables_javascript_is_available(self, client, owner):
        response = client.get("/static/js/tables.js")

        assert response.status_code == 200
        assert b"loadTables" in response.data

    def test_table_page_contains_filters(self, client, owner):
        response = client.get("/tables")

        assert b"table-search" in response.data
        assert b"status-filter" in response.data
        assert b"active-filter" in response.data

    def test_owner_can_view_empty_table_list(self, client, owner):
        response = client.get("/api/tables")

        assert response.status_code == 200
        assert response.get_json() == []

    def test_owner_can_create_table_and_view_it(self, client, owner):
        create_response = client.post(
            "/api/tables",
            json={
                "table_number": "T-101",
                "capacity": 4,
                "status": "available",
                "is_active": True
            }
        )

        assert create_response.status_code == 201

        created_table = create_response.get_json()["table"]

        assert created_table["table_number"] == "T-101"
        assert created_table["capacity"] == 4
        assert created_table["status"] == "available"

        list_response = client.get("/api/tables")

        assert list_response.status_code == 200
        assert len(list_response.get_json()) == 1

    def test_owner_can_update_table(self, client, owner):
        create_response = client.post(
            "/api/tables",
            json={
                "table_number": "T-102",
                "capacity": 2,
                "status": "available",
                "is_active": True
            }
        )

        table_id = create_response.get_json()["table"]["id"]

        update_response = client.put(
            f"/api/tables/{table_id}",
            json={
                "table_number": "T-102",
                "capacity": 6,
                "status": "reserved",
                "is_active": True
            }
        )

        assert update_response.status_code == 200

        updated_table = update_response.get_json()["table"]

        assert updated_table["capacity"] == 6
        assert updated_table["status"] == "reserved"

    def test_owner_can_change_table_status(self, client, owner):
        create_response = client.post(
            "/api/tables",
            json={
                "table_number": "T-103",
                "capacity": 4,
                "status": "available",
                "is_active": True
            }
        )

        table_id = create_response.get_json()["table"]["id"]

        status_response = client.patch(
            f"/api/tables/{table_id}/status",
            json={
                "status": "occupied"
            }
        )

        assert status_response.status_code == 200
        assert status_response.get_json()["table"]["status"] == "occupied"

    def test_invalid_table_status_is_rejected(self, client, owner):
        response = client.post(
            "/api/tables",
            json={
                "table_number": "T-104",
                "capacity": 4,
                "status": "broken",
                "is_active": True
            }
        )

        assert response.status_code == 400

    def test_invalid_capacity_is_rejected(self, client, owner):
        response = client.post(
            "/api/tables",
            json={
                "table_number": "T-105",
                "capacity": 0,
                "status": "available",
                "is_active": True
            }
        )

        assert response.status_code == 400

    def test_nonexistent_table_returns_404(self, client, owner):
        response = client.get("/api/tables/99999")

        assert response.status_code == 404