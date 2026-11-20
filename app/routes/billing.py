from decimal import Decimal

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.extensions import db
from app.models import RestaurantOrder


billing_bp = Blueprint("billing", __name__)

BILLING_ROLES = {
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "cashier",
    "accountant",
    "system_administrator"
}


@billing_bp.route("/billing/orders/<int:order_id>", methods=["GET"])
@login_required
def get_order_bill(order_id):

    if current_user.role not in BILLING_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to access billing"
        }), 403

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    items = []

    for item in order.items:
        unit_price = Decimal(str(item.unit_price))
        line_total = Decimal(str(item.line_total))

        items.append({
            "menu_item_id": item.menu_item_id,
            "item_name": item.menu_item.name,
            "quantity": item.quantity,
            "unit_price": float(unit_price),
            "line_total": float(line_total)
        })

    subtotal = Decimal(str(order.subtotal))
    discount = Decimal(str(order.discount_amount))
    tax = Decimal(str(order.tax_amount))

    amount_payable = subtotal + tax - discount

    bill = {
        "order_id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "order_type": order.order_type,
        "order_status": order.status,
        "items": items,
        "subtotal": float(subtotal),
        "discount_amount": float(discount),
        "tax_amount": float(tax),
        "amount_payable": float(amount_payable)
    }

    return jsonify({
        "status": "success",
        "message": "Bill retrieved successfully",
        "bill": bill
    }), 200