
from flask import Blueprint, jsonify
from flask_login import current_user

from app.dashboards import DASHBOARD_CONFIG
from app.permissions import permission_required


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard", methods=["GET"])
@permission_required("dashboard.view")
def get_dashboard():

    user_role = current_user.role

    dashboard = DASHBOARD_CONFIG.get(user_role)

    if dashboard is None:
        return jsonify({
            "status": "error",
            "message": "Dashboard configuration not found"
        }), 404

    return jsonify({
        "status": "success",
        "username": current_user.username,
        "role": user_role,
        "dashboard": dashboard
    }), 200
