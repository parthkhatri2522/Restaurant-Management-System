
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import (
    RestaurantOrder,
    OrderItem,
    MenuItem,
    RestaurantTable,
    Reservation
)


orders_bp = Blueprint("orders", __name__)


ALLOWED_ROLES = {
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "cashier",
    "waiter",
    "head_chef",
    "kitchen_staff",
    "quality_officer",
    "system_administrator"
}

ORDER_STATUSES = {
    "pending",
    "confirmed",
    "preparing",
    "ready",
    "served",
    "completed",
    "cancelled"
}

ORDER_TYPES = {"dine_in", "takeaway", "delivery"}


def check_access():
    if current_user.role not in ALLOWED_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to access orders"
        }), 403
    return None


def serialize_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "order_type": order.order_type,
        "status": order.status,
        "table_id": order.table_id,
        "reservation_id": order.reservation_id,
        "subtotal": float(order.subtotal),
        "tax_amount": float(order.tax_amount),
        "discount_amount": float(order.discount_amount),
        "total_amount": float(order.total_amount),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "menu_item_name": item.menu_item.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "line_total": float(item.line_total),
                "special_instructions": item.special_instructions
            }
            for item in order.items
        ]
    }


def validate_order_items(items):
    if not isinstance(items, list) or not items:
        return None, "At least one order item is required"

    validated_items = []
    subtotal = Decimal("0.00")

    for entry in items:
        if not isinstance(entry, dict):
            return None, "Each order item must be an object"

        try:
            menu_item_id = int(entry.get("menu_item_id"))
            quantity = int(entry.get("quantity"))
        except (TypeError, ValueError):
            return None, "Valid menu item ID and quantity are required"

        if quantity <= 0:
            return None, "Quantity must be greater than zero"

        menu_item = db.session.get(MenuItem, menu_item_id)

        if menu_item is None:
            return None, f"Menu item {menu_item_id} does not exist"

        if not menu_item.is_available:
            return None, f"{menu_item.name} is currently unavailable"

        unit_price = Decimal(str(menu_item.price))
        line_total = unit_price * quantity
        subtotal += line_total

        validated_items.append({
            "menu_item": menu_item,
            "quantity": quantity,
            "unit_price": unit_price,
            "line_total": line_total,
            "special_instructions": entry.get("special_instructions")
        })

    return {
        "items": validated_items,
        "subtotal": subtotal
    }, None


@orders_bp.route("/orders", methods=["GET"])
@login_required
def get_orders():
    access_error = check_access()
    if access_error:
        return access_error

    query = RestaurantOrder.query

    status = request.args.get("status")
    order_type = request.args.get("order_type")

    if status:
        if status not in ORDER_STATUSES:
            return jsonify({
                "status": "error",
                "message": "Invalid order status"
            }), 400
        query = query.filter_by(status=status)

    if order_type:
        if order_type not in ORDER_TYPES:
            return jsonify({
                "status": "error",
                "message": "Invalid order type"
            }), 400
        query = query.filter_by(order_type=order_type)

    orders = query.order_by(
        RestaurantOrder.created_at.desc()
    ).all()

    return jsonify({
        "status": "success",
        "count": len(orders),
        "orders": [serialize_order(order) for order in orders]
    }), 200


@orders_bp.route("/orders", methods=["POST"])
@login_required
def create_order():
    access_error = check_access()
    if access_error:
        return access_error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON request body is required"
        }), 400

    validated, error = validate_order_items(data.get("items"))

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    order_type = data.get("order_type", "dine_in")

    if order_type not in ORDER_TYPES:
        return jsonify({
            "status": "error",
            "message": "Invalid order type"
        }), 400

    try:
        discount = Decimal(str(data.get("discount_amount", 0)))
    except (InvalidOperation, ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Invalid discount amount"
        }), 400

    subtotal = validated["subtotal"]

    if discount < 0 or discount > subtotal:
        return jsonify({
            "status": "error",
            "message": "Discount must be between zero and the subtotal"
        }), 400

    table_id = data.get("table_id")
    reservation_id = data.get("reservation_id")

    if table_id is not None:
        table = db.session.get(RestaurantTable, table_id)
        if table is None:
            return jsonify({
                "status": "error",
                "message": "Dining table does not exist"
            }), 400

    if reservation_id is not None:
        reservation = db.session.get(Reservation, reservation_id)
        if reservation is None:
            return jsonify({
                "status": "error",
                "message": "Reservation does not exist"
            }), 400

    order = RestaurantOrder(
        order_number=f"ORD-{uuid4().hex[:12].upper()}",
        customer_name=data.get("customer_name"),
        order_type=order_type,
        status="pending",
        table_id=table_id,
        reservation_id=reservation_id,
        subtotal=subtotal,
        tax_amount=Decimal("0.00"),
        discount_amount=discount,
        total_amount=subtotal - discount
    )

    try:
        db.session.add(order)
        db.session.flush()

        for entry in validated["items"]:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=entry["menu_item"].id,
                quantity=entry["quantity"],
                unit_price=entry["unit_price"],
                line_total=entry["line_total"],
                special_instructions=entry["special_instructions"]
            )
            db.session.add(order_item)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Order created successfully",
            "order": serialize_order(order)
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Unable to create order"
        }), 500


@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):
    access_error = check_access()
    if access_error:
        return access_error

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    return jsonify({
        "status": "success",
        "order": serialize_order(order)
    }), 200


@orders_bp.route("/orders/<int:order_id>", methods=["PUT"])
@login_required
def update_order(order_id):
    access_error = check_access()
    if access_error:
        return access_error

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    if order.status in {"completed", "cancelled"}:
        return jsonify({
            "status": "error",
            "message": "Completed or cancelled orders cannot be edited"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON request body is required"
        }), 400

    if "customer_name" in data:
        order.customer_name = data["customer_name"]

    if "items" in data:
        validated, error = validate_order_items(data["items"])

        if error:
            return jsonify({
                "status": "error",
                "message": error
            }), 400

        for item in list(order.items):
            db.session.delete(item)

        db.session.flush()

        for entry in validated["items"]:
            db.session.add(OrderItem(
                order_id=order.id,
                menu_item_id=entry["menu_item"].id,
                quantity=entry["quantity"],
                unit_price=entry["unit_price"],
                line_total=entry["line_total"],
                special_instructions=entry["special_instructions"]
            ))

        order.subtotal = validated["subtotal"]

    if "discount_amount" in data:
        try:
            discount = Decimal(str(data["discount_amount"]))
        except (InvalidOperation, ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Invalid discount amount"
            }), 400

        if discount < 0 or discount > order.subtotal:
            return jsonify({
                "status": "error",
                "message": "Invalid discount amount"
            }), 400

        order.discount_amount = discount

    order.total_amount = (
        order.subtotal
        + order.tax_amount
        - order.discount_amount
    )

    try:
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Order updated successfully",
            "order": serialize_order(order)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Unable to update order"
        }), 500


@orders_bp.route("/orders/<int:order_id>/status", methods=["PATCH"])
@login_required
def update_order_status(order_id):
    access_error = check_access()
    if access_error:
        return access_error

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

    if new_status not in ORDER_STATUSES:
        return jsonify({
            "status": "error",
            "message": "Invalid order status"
        }), 400

    order.status = new_status

    try:
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Order status updated successfully",
            "order": serialize_order(order)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Unable to update order status"
        }), 500