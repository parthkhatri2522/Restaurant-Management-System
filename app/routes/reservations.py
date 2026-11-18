
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.extensions import db
from app.permissions import role_required
from app.models import Reservation, RestaurantTable


reservations_bp = Blueprint("reservations", __name__)

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
    "host"
)

VALID_STATUSES = {
    "pending",
    "confirmed",
    "cancelled",
    "completed"
}


def serialize_reservation(reservation):
    return {
        column.name: (
            getattr(reservation, column.name).isoformat()
            if isinstance(getattr(reservation, column.name), (datetime,))
            else getattr(reservation, column.name)
        )
        for column in Reservation.__table__.columns
    }


@reservations_bp.route("/reservations", methods=["GET"])
@login_required
@role_required(*VIEW_ROLES)
def get_reservations():
    query = Reservation.query

    date_filter = request.args.get("date")
    status_filter = request.args.get("status")

    if date_filter:
        try:
            selected_date = datetime.strptime(
                date_filter, "%Y-%m-%d"
            ).date()
            query = query.filter(
                db.func.date(Reservation.reservation_time) == selected_date
            )
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    if status_filter:
        if status_filter not in VALID_STATUSES:
            return jsonify({"error": "Invalid reservation status"}), 400
        query = query.filter_by(status=status_filter)

    reservations = query.order_by(
        Reservation.reservation_time
    ).all()

    return jsonify([
        serialize_reservation(reservation)
        for reservation in reservations
    ]), 200


@reservations_bp.route("/reservations/<int:reservation_id>", methods=["GET"])
@login_required
@role_required(*VIEW_ROLES)
def get_reservation(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    return jsonify(serialize_reservation(reservation)), 200


@reservations_bp.route("/reservations", methods=["POST"])
@login_required
@role_required(*MANAGE_ROLES)
def create_reservation():
    data = request.get_json() or {}

    required_fields = [
        "customer_name",
        "customer_phone",
        "reservation_time",
        "party_size"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    try:
        reservation_time = datetime.fromisoformat(
            data["reservation_time"]
        )
        party_size = int(data["party_size"])

        if party_size <= 0:
            return jsonify({"error": "Party size must be greater than zero"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "Invalid reservation time or party size"}), 400

    table_id = data.get("table_id")

    if table_id is not None:
        table = db.session.get(RestaurantTable, table_id)

        if not table:
            return jsonify({"error": "Dining table not found"}), 404

        if not table.is_active:
            return jsonify({"error": "Dining table is inactive"}), 400

        if party_size > table.capacity:
            return jsonify({"error": "Party size exceeds table capacity"}), 400

    reservation = Reservation(
        customer_name=data["customer_name"].strip(),
        customer_phone=data["customer_phone"].strip(),
        reservation_time=reservation_time,
        party_size=party_size,
        table_id=table_id,
        status="pending"
    )

    db.session.add(reservation)
    db.session.commit()

    return jsonify({
        "message": "Reservation created successfully",
        "reservation": serialize_reservation(reservation)
    }), 201


@reservations_bp.route(
    "/reservations/<int:reservation_id>",
    methods=["PUT"]
)
@login_required
@role_required(*MANAGE_ROLES)
def update_reservation(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json() or {}

    if "customer_name" in data:
        if not data["customer_name"].strip():
            return jsonify({"error": "Customer name cannot be empty"}), 400
        reservation.customer_name = data["customer_name"].strip()

    if "customer_phone" in data:
        reservation.customer_phone = data["customer_phone"].strip()

    if "reservation_time" in data:
        try:
            reservation.reservation_time = datetime.fromisoformat(
                data["reservation_time"]
            )
        except ValueError:
            return jsonify({"error": "Invalid reservation time"}), 400

    if "party_size" in data:
        try:
            party_size = int(data["party_size"])
            if party_size <= 0:
                return jsonify({"error": "Party size must be greater than zero"}), 400
            reservation.party_size = party_size
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid party size"}), 400

    if "table_id" in data:
        table_id = data["table_id"]

        if table_id is not None:
            table = db.session.get(RestaurantTable, table_id)

            if not table:
                return jsonify({"error": "Dining table not found"}), 404

            if not table.is_active:
                return jsonify({"error": "Dining table is inactive"}), 400

            if reservation.party_size > table.capacity:
                return jsonify({"error": "Party size exceeds table capacity"}), 400

        reservation.table_id = table_id

    db.session.commit()

    return jsonify({
        "message": "Reservation updated successfully",
        "reservation": serialize_reservation(reservation)
    }), 200


@reservations_bp.route(
    "/reservations/<int:reservation_id>/status",
    methods=["PATCH"]
)
@login_required
@role_required(*MANAGE_ROLES)
def update_reservation_status(reservation_id):
    reservation = db.session.get(Reservation, reservation_id)

    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json() or {}
    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({
            "error": "Invalid reservation status",
            "valid_statuses": sorted(VALID_STATUSES)
        }), 400

    reservation.status = status
    db.session.commit()

    return jsonify({
        "message": "Reservation status updated successfully",
        "reservation": serialize_reservation(reservation)
    }), 200