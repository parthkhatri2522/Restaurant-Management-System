import pytest

from app import create_app
from app.extensions import db
from app.permissions import has_permission


@pytest.fixture
def app():
    application = create_app()
    application.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SECRET_KEY="test-secret-key"
    )

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_orders_page_requires_login(client):
    response = client.get("/orders")
    assert response.status_code in (302, 401)


def test_orders_route_is_registered(app):
    routes = {
        rule.rule for rule in app.url_map.iter_rules()
    }
    assert "/orders" in routes


def test_orders_css_is_available(client):
    response = client.get("/static/css/orders.css")
    assert response.status_code == 200
    assert b".orders-page" in response.data
    assert b".order-statistics" in response.data


def test_orders_javascript_is_available(client):
    response = client.get("/static/js/orders.js")
    assert response.status_code == 200
    assert b"/api/orders" in response.data
    assert b"loadOrders" in response.data


def test_order_roles_have_order_view_permission():
    for role in (
        "general_manager",
        "assistant_manager",
        "cashier",
        "waiter"
    ):
        assert has_permission(role, "orders.view")


def test_order_creation_roles_can_view_menu():
    for role in (
        "general_manager",
        "assistant_manager",
        "cashier",
        "waiter"
    ):
        assert has_permission(role, "menu.view")


def test_accountant_does_not_have_order_view_permission():
    assert not has_permission("accountant", "orders.view")