from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

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
    return render_template("dashboard_placeholder.html")