import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_billing_page_requires_login(client):
    response = client.get("/billing")
    assert response.status_code in (302, 401)


def test_billing_route_is_registered(client):
    rules = {rule.rule for rule in client.application.url_map.iter_rules()}
    assert "/billing" in rules


def test_billing_css_is_available(client):
    response = client.get("/static/css/billing.css")
    assert response.status_code == 200


def test_billing_javascript_is_available(client):
    response = client.get("/static/js/billing.js")
    assert response.status_code == 200


def test_billing_template_contains_order_and_payment_sections(client):
    response = client.get("/billing")

    # The login page may be returned because this is an unauthenticated request.
    # Render the template inside a request context for template-content checks.
    with client.application.test_request_context("/billing"):
        from flask import render_template
        html = render_template("billing.html")

    assert "Billing" in html
    assert "Bill details" in html
    assert "Payment summary" in html
    assert "Payment history" in html
    assert "Record a payment" in html


def test_billing_javascript_uses_existing_api_endpoints(client):
    response = client.get("/static/js/billing.js")
    source = response.get_data(as_text=True)

    assert "/api/orders" in source
    assert "/api/billing/orders/" in source
    assert "/api/payments/orders/" in source
    assert "/api/payments/" in source


def test_billing_template_loads_billing_assets(client):
    with client.application.test_request_context("/billing"):
        from flask import render_template
        html = render_template("billing.html")

    assert "css/billing.css" in html
    assert "js/billing.js" in html