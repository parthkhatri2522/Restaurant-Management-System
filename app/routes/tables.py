
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.extensions import db
from app.permissions import role_required
from app.models import RestaurantTable

tables_bp = Blueprint("tables", __name__)

VIEW_ROLES = (
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "host",
    "system_administrator"
)

MANAGE_ROLES = (
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "system_administrator"
)

VALID_STATUSES = {
    "available",
    "occupied",
    "reserved",
    "maintenance"
}


def serialize_table(table):
    return {
        column.name: getattr(table, column.name)
        for column in RestaurantTable.__table__.columns
    }


@tables_bp.route("/tables", methods=["GET"])
@login_required
@role_required(*VIEW_ROLES)
def get_tables():
    tables = RestaurantTable.query.order_by(
        RestaurantTable.id
    ).all()

    return jsonify([
        serialize_table(table)
        for table in tables
    ]), 200


@tables_bp.route("/tables/<int:table_id>", methods=["GET"])
@login_required
@role_required(*VIEW_ROLES)
def get_table(table_id):
    table = db.session.get(RestaurantTable, table_id)

    if not table:
        return jsonify({"error": "Table not found"}), 404

    return jsonify(serialize_table(table)), 200


@tables_bp.route("/tables", methods=["POST"])
@login_required
@role_required(*MANAGE_ROLES)
def create_table():
    data = request.get_json() or {}

    allowed_fields = {
        "table_number",
        "capacity",
        "status",
        "location",
        "is_active"
    }

    table_data = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    if not table_data.get("table_number"):
        return jsonify({
            "error": "Table number is required"
        }), 400

    if "capacity" in table_data:
        try:
            table_data["capacity"] = int(table_data["capacity"])
            if table_data["capacity"] <= 0:
                return jsonify({
                    "error": "Capacity must be greater than zero"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "error": "Invalid table capacity"
            }), 400

    if "status" in table_data:
        if table_data["status"] not in VALID_STATUSES:
            return jsonify({
                "error": "Invalid table status"
            }), 400

    table = RestaurantTable(**table_data)

    db.session.add(table)
    db.session.commit()

    return jsonify({
        "message": "Dining table created successfully",
        "table": serialize_table(table)
    }), 201


@tables_bp.route("/tables/<int:table_id>", methods=["PUT"])
@login_required
@role_required(*MANAGE_ROLES)
def update_table(table_id):
    table = db.session.get(RestaurantTable, table_id)

    if not table:
        return jsonify({"error": "Table not found"}), 404

    data = request.get_json() or {}

    allowed_fields = {
        "table_number",
        "capacity",
        "status",
        "location",
        "is_active"
    }

    for field, value in data.items():
        if field not in allowed_fields:
            continue

        if field == "capacity":
            try:
                value = int(value)
                if value <= 0:
                    return jsonify({
                        "error": "Capacity must be greater than zero"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "error": "Invalid table capacity"
                }), 400

        if field == "status" and value not in VALID_STATUSES:
            return jsonify({
                "error": "Invalid table status"
            }), 400

        setattr(table, field, value)

    db.session.commit()

    return jsonify({
        "message": "Dining table updated successfully",
        "table": serialize_table(table)
    }), 200


@tables_bp.route("/tables/<int:table_id>/status", methods=["PATCH"])
@login_required
@role_required(*MANAGE_ROLES)
def update_table_status(table_id):
    table = db.session.get(RestaurantTable, table_id)

    if not table:
        return jsonify({"error": "Table not found"}), 404

    data = request.get_json() or {}
    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid table status",
            "valid_statuses": sorted(VALID_STATUSES)
        }), 400

    table.status = status
    db.session.commit()

    return jsonify({
        "message": "Table status updated successfully",
        "table": serialize_table(table)
    }), 200
