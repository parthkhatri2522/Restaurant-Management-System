from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models import RestaurantOrder


kitchen_bp = Blueprint("kitchen", __name__)

KITCHEN_VIEW_ROLES = {
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "head_chef",
    "kitchen_staff",
    "quality_officer",
    "system_administrator"
}

KITCHEN_UPDATE_ROLES = {
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "head_chef",
    "kitchen_staff",
    "system_administrator"
}

KITCHEN_QUEUE_STATUSES = [
    "pending",
    "confirmed",
    "preparing",
    "ready"
]


def serialize_kitchen_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "order_type": order.order_type,
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "menu_item_id": item.menu_item_id,
                "name": item.menu_item.name,
                "quantity": item.quantity,
                "special_instructions": item.special_instructions
            }
            for item in order.items
        ]
    }


@kitchen_bp.route("/kitchen/orders", methods=["GET"])
@login_required
def get_kitchen_orders():
    if current_user.role not in KITCHEN_VIEW_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to view kitchen orders"
        }), 403

    query = RestaurantOrder.query.filter(
        RestaurantOrder.status.in_(KITCHEN_QUEUE_STATUSES)
    )

    requested_status = request.args.get("status")

    if requested_status:
        if requested_status not in KITCHEN_QUEUE_STATUSES:
            return jsonify({
                "status": "error",
                "message": "Invalid kitchen order status"
            }), 400

        query = query.filter_by(status=requested_status)

    orders = query.order_by(
        RestaurantOrder.created_at.asc()
    ).all()

    return jsonify({
        "status": "success",
        "count": len(orders),
        "orders": [
            serialize_kitchen_order(order)
            for order in orders
        ]
    }), 200


@kitchen_bp.route(
    "/kitchen/orders/<int:order_id>/status",
    methods=["PATCH"]
)
@login_required
def update_kitchen_order_status(order_id):
    if current_user.role not in KITCHEN_UPDATE_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to update kitchen orders"
        }), 403

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON request body is required"
        }), 400

    new_status = data.get("status")

    allowed_transitions = {
        "pending": {"preparing"},
        "confirmed": {"preparing"},
        "preparing": {"ready"}
    }

    permitted_next_statuses = allowed_transitions.get(
        order.status,
        set()
    )

    if new_status not in permitted_next_statuses:
        return jsonify({
            "status": "error",
            "message": (
                f"Cannot change order status from "
                f"{order.status} to {new_status}"
            )
        }), 400

    order.status = new_status

    try:
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Kitchen order status updated successfully",
            "order": serialize_kitchen_order(order)
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Unable to update kitchen order status"
        }), 500