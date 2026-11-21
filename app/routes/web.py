from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user, login_required

from app.dashboards import DASHBOARD_CONFIG


web_bp = Blueprint("web", __name__)


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