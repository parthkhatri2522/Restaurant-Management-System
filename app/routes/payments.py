from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import RestaurantOrder, Payment


payments_bp = Blueprint("payments", __name__)

PAYMENT_ROLES = {
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "cashier",
    "accountant",
    "system_administrator"
}

PAYMENT_METHODS = {"cash", "card", "upi", "online"}
PAYMENT_STATUSES = {"pending", "completed", "failed", "refunded"}

CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value or 0)).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


def payment_response(payment):
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": float(payment.amount),
        "payment_method": payment.payment_method,
        "status": payment.status,
        "transaction_reference": payment.transaction_reference,
        "paid_at": (
            payment.paid_at.isoformat()
            if payment.paid_at else None
        ),
        "created_at": (
            payment.created_at.isoformat()
            if payment.created_at else None
        )
    }


def get_payment_summary(order):
    payments = Payment.query.filter_by(
        order_id=order.id
    ).order_by(Payment.id.asc()).all()

    total_amount = money(order.total_amount)

    completed_amount = money(
        sum(
            (
                money(payment.amount)
                for payment in payments
                if payment.status == "completed"
            ),
            Decimal("0.00")
        )
    )

    refunded_amount = money(
        sum(
            (
                money(payment.amount)
                for payment in payments
                if payment.status == "refunded"
            ),
            Decimal("0.00")
        )
    )

    # Refunded payments are no longer counted as completed.
    net_paid = completed_amount
    outstanding = money(total_amount - net_paid)

    if outstanding < 0:
        outstanding = Decimal("0.00")

    if outstanding == 0 and total_amount > 0:
        payment_status = "paid"
    elif net_paid > 0:
        payment_status = "partially_paid"
    else:
        payment_status = "unpaid"

    return {
        "order_total": float(total_amount),
        "completed_payments": float(completed_amount),
        "refunded_payments": float(refunded_amount),
        "net_paid": float(net_paid),
        "outstanding_balance": float(outstanding),
        "payment_status": payment_status
    }


@payments_bp.route(
    "/payments/orders/<int:order_id>",
    methods=["POST"]
)
@login_required
def create_payment(order_id):

    if current_user.role not in PAYMENT_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to record payments"
        }), 403

    data = request.get_json(silent=True) or {}

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    if order.status == "cancelled":
        return jsonify({
            "status": "error",
            "message": "Payments cannot be recorded for cancelled orders"
        }), 400

    try:
        amount = Decimal(str(data.get("amount", ""))).quantize(
            CENT,
            rounding=ROUND_HALF_UP
        )
    except Exception:
        return jsonify({
            "status": "error",
            "message": "A valid payment amount is required"
        }), 400

    if not amount.is_finite() or amount <= 0:
        return jsonify({
            "status": "error",
            "message": "Payment amount must be greater than zero"
        }), 400

    payment_method = (
        data.get("payment_method") or ""
    ).strip().lower()

    if payment_method not in PAYMENT_METHODS:
        return jsonify({
            "status": "error",
            "message": "Invalid payment method. Use cash, card, upi or online"
        }), 400

    transaction_reference = (
        data.get("transaction_reference") or ""
    ).strip()

    if transaction_reference and len(transaction_reference) > 120:
        return jsonify({
            "status": "error",
            "message": "Transaction reference cannot exceed 120 characters"
        }), 400

    if payment_method != "cash" and not transaction_reference:
        return jsonify({
            "status": "error",
            "message": "A transaction reference is required for digital payments"
        }), 400

    if transaction_reference:
        existing_reference = Payment.query.filter_by(
            transaction_reference=transaction_reference
        ).first()

        if existing_reference:
            return jsonify({
                "status": "error",
                "message": "Transaction reference already exists"
            }), 409

    summary = get_payment_summary(order)
    outstanding = money(summary["outstanding_balance"])

    if amount > outstanding:
        return jsonify({
            "status": "error",
            "message": "Payment amount exceeds the outstanding balance",
            "outstanding_balance": float(outstanding)
        }), 400

    payment_status = (
        "completed"
        if payment_method == "cash"
        else "pending"
    )

    payment = Payment(
        order_id=order.id,
        amount=amount,
        payment_method=payment_method,
        status=payment_status,
        transaction_reference=transaction_reference or None,
        paid_at=(
            datetime.utcnow()
            if payment_status == "completed"
            else None
        )
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Payment recorded successfully",
        "payment": payment_response(payment),
        "payment_summary": get_payment_summary(order)
    }), 201


@payments_bp.route(
    "/payments/orders/<int:order_id>",
    methods=["GET"]
)
@login_required
def get_order_payments(order_id):

    if current_user.role not in PAYMENT_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to view payments"
        }), 403

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    payments = Payment.query.filter_by(
        order_id=order.id
    ).order_by(Payment.id.asc()).all()

    return jsonify({
        "status": "success",
        "order_id": order.id,
        "payments": [
            payment_response(payment)
            for payment in payments
        ],
        "payment_summary": get_payment_summary(order)
    }), 200


@payments_bp.route(
    "/payments/<int:payment_id>/status",
    methods=["PATCH"]
)
@login_required
def update_payment_status(payment_id):

    if current_user.role not in PAYMENT_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to update payment status"
        }), 403

    payment = db.session.get(Payment, payment_id)

    if payment is None:
        return jsonify({
            "status": "error",
            "message": "Payment not found"
        }), 404

    data = request.get_json(silent=True) or {}
    new_status = (
        data.get("status") or ""
    ).strip().lower()

    if new_status not in PAYMENT_STATUSES:
        return jsonify({
            "status": "error",
            "message": "Invalid payment status"
        }), 400

    allowed_transitions = {
        "pending": {"completed", "failed"},
        "completed": {"refunded"},
        "failed": set(),
        "refunded": set()
    }

    if new_status not in allowed_transitions[payment.status]:
        return jsonify({
            "status": "error",
            "message": (
                f"Payment cannot move from {payment.status} "
                f"to {new_status}"
            )
        }), 400

    if new_status == "completed":
        order = db.session.get(
            RestaurantOrder,
            payment.order_id
        )

        summary = get_payment_summary(order)
        outstanding = money(summary["outstanding_balance"])

        if money(payment.amount) > outstanding:
            return jsonify({
                "status": "error",
                "message": "Payment exceeds the remaining balance"
            }), 400

        payment.paid_at = datetime.utcnow()

    payment.status = new_status

    db.session.commit()

    order = db.session.get(
        RestaurantOrder,
        payment.order_id
    )

    return jsonify({
        "status": "success",
        "message": "Payment status updated successfully",
        "payment": payment_response(payment),
        "payment_summary": get_payment_summary(order)
    }), 200