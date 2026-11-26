from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    file_path = PROJECT_ROOT / relative_path
    assert file_path.exists(), f"Missing project file: {relative_path}"
    return file_path.read_text(encoding="utf-8")


def test_kitchen_page_route_exists():
    source = read_project_file("app/routes/web.py")

    assert '@web_bp.route("/kitchen", methods=["GET"])' in source
    assert "def kitchen_page():" in source
    assert 'return render_template("kitchen.html")' in source


def test_kitchen_page_requires_login_and_role():
    source = read_project_file("app/routes/web.py")

    route_section = source.split('def kitchen_page():')[0]

    assert "@login_required" in route_section
    assert "@role_required(*KITCHEN_VIEW_ROLES)" in route_section


def test_kitchen_view_roles_are_defined():
    source = read_project_file("app/routes/web.py")

    assert "KITCHEN_VIEW_ROLES = (" in source
    assert '"restaurant_owner"' in source
    assert '"general_manager"' in source
    assert '"assistant_manager"' in source
    assert '"head_chef"' in source
    assert '"kitchen_staff"' in source
    assert '"quality_officer"' in source
    assert '"system_administrator"' in source


def test_kitchen_template_exists_and_extends_base():
    source = read_project_file("app/templates/kitchen.html")

    assert '{% extends "base.html" %}' in source
    assert "Kitchen Order Management" in source
    assert 'data-user-role="{{ current_user.role }}"' in source


def test_kitchen_template_contains_order_management_controls():
    source = read_project_file("app/templates/kitchen.html")

    assert 'id="refresh-orders-button"' in source
    assert 'id="status-filter"' in source
    assert 'id="order-search"' in source
    assert 'id="kitchen-orders-list"' in source
    assert 'id="pending-count"' in source
    assert 'id="preparing-count"' in source


def test_kitchen_css_exists_and_contains_responsive_styles():
    source = read_project_file("app/static/css/kitchen.css")

    assert ".kitchen-page" in source
    assert ".kitchen-order-card" in source
    assert ".order-action-button" in source
    assert "@media (max-width: 600px)" in source


def test_kitchen_javascript_uses_existing_api_endpoints():
    source = read_project_file("app/static/js/kitchen.js")

    assert '"/api/kitchen/orders"' in source
    assert "/api/kitchen/orders/" in source
    assert "method: \"PATCH\"" in source


def test_kitchen_javascript_supports_order_status_workflow():
    source = read_project_file("app/static/js/kitchen.js")

    assert '"pending"' in source
    assert '"confirmed"' in source
    assert '"preparing"' in source
    assert '"ready"' in source
    assert "Start Preparing" in source
    assert "Mark Ready" in source


def test_kitchen_javascript_displays_special_instructions():
    source = read_project_file("app/static/js/kitchen.js")

    assert "special_instructions" in source
    assert "Special Instructions" in source


def test_kitchen_javascript_has_view_only_role_support():
    source = read_project_file("app/static/js/kitchen.js")

    assert '"quality_officer"' not in source
    assert "canUpdateOrders" in source
    assert "View-only access" in source