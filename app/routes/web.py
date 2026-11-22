from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user, login_required

from app.dashboards import DASHBOARD_CONFIG
from app.permissions import permission_required, role_required


web_bp = Blueprint("web", __name__)


TABLE_VIEW_ROLES = (
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "host",
    "system_administrator"
)

RESERVATION_VIEW_ROLES = (
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "host",
    "system_administrator"
)


@web_bp.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@web_bp.route("/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard_page"))

    return render_template("login.html")


@web_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard_page():
    user_role = current_user.role
    dashboard = DASHBOARD_CONFIG.get(user_role)

    if dashboard is None:
        abort(404)

    return render_template(
        "dashboard.html",
        dashboard=dashboard,
        user_role=user_role
    )


@web_bp.route("/employees", methods=["GET"])
@permission_required("employees.view")
def employees_page():
    return render_template("employees.html")


@web_bp.route("/tables", methods=["GET"])
@role_required(*TABLE_VIEW_ROLES)
def tables_page():
    return render_template("tables.html")


@web_bp.route("/reservations", methods=["GET"])
@login_required
@role_required(*RESERVATION_VIEW_ROLES)
def reservations_page():
    return render_template("reservations.html")