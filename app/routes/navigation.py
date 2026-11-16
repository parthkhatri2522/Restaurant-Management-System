
from flask import Blueprint, jsonify
from flask_login import current_user

from app.navigation import NAVIGATION_CONFIG
from app.permissions import has_permission, permission_required


navigation_bp = Blueprint("navigation", __name__)


@navigation_bp.route("/api/navigation", methods=["GET"])
@permission_required("dashboard.view")
def get_navigation():

    # Identify the authenticated user's role
    user_role = current_user.role

    # Retrieve navigation configuration for that role
    navigation_items = NAVIGATION_CONFIG.get(user_role)

    if navigation_items is None:
        return jsonify({
            "status": "error",
            "message": "Navigation configuration not found"
        }), 404

    # Display only items permitted for this user
    accessible_items = [
        {
            "id": item["id"],
            "label": item["label"],
            "icon": item["icon"],
            "url": item["url"]
        }
        for item in navigation_items
        if has_permission(user_role, item["permission"])
    ]

    return jsonify({
        "status": "success",
        "username": current_user.username,
        "role": user_role,
        "navigation": accessible_items
    }), 200
