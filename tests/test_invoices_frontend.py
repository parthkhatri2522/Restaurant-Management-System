from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    file_path = PROJECT_ROOT / relative_path
    assert file_path.exists(), f"Missing project file: {relative_path}"
    return file_path.read_text(encoding="utf-8")


def test_invoice_page_route_exists():
    source = read_project_file("app/routes/web.py")

    assert '@web_bp.route("/invoices", methods=["GET"])' in source
    assert "def invoices_page():" in source
    assert 'return render_template("invoices.html")' in source


def test_invoice_page_requires_login_and_role():
    source = read_project_file("app/routes/web.py")

    route_section = source.split('def invoices_page():')[0]

    assert "@login_required" in route_section
    assert "@role_required(*INVOICE_VIEW_ROLES)" in route_section


def test_invoice_view_roles_are_defined():
    source = read_project_file("app/routes/web.py")

    assert "INVOICE_VIEW_ROLES = (" in source
    assert '"restaurant_owner"' in source
    assert '"general_manager"' in source
    assert '"cashier"' in source
    assert '"accountant"' in source
    assert '"system_administrator"' in source


def test_invoice_template_exists_and_extends_base():
    source = read_project_file("app/templates/invoices.html")

    assert '{% extends "base.html" %}' in source
    assert "GST & Invoice Management" in source
    assert 'id="gst-config-form"' in source
    assert 'data-user-role="{{ current_user.role }}"' in source


def test_invoice_template_contains_main_sections():
    source = read_project_file("app/templates/invoices.html")

    assert 'id="generate-invoice-form"' in source
    assert 'id="lookup-invoice-form"' in source
    assert 'id="invoice-result-section"' in source
    assert 'id="invoice-items-body"' in source
    assert 'id="print-invoice-button"' in source


def test_invoice_css_exists_and_contains_responsive_and_print_styles():
    source = read_project_file("app/static/css/invoices.css")

    assert ".invoice-page" in source
    assert ".invoice-document" in source
    assert "@media (max-width: 700px)" in source
    assert "@media print" in source


def test_invoice_javascript_contains_required_api_endpoints():
    source = read_project_file("app/static/js/invoices.js")

    assert "/api/gst/configuration" in source
    assert "/api/invoices/orders/" in source
    assert "/api/invoices/" in source


def test_invoice_javascript_contains_core_actions():
    source = read_project_file("app/static/js/invoices.js")

    assert "generateInvoice" in source
    assert "renderInvoice" in source
    assert "window.print()" in source
    assert "is_gst_registered" in source
    assert "cgst_amount" in source
    assert "sgst_amount" in source
    assert "igst_amount" in source