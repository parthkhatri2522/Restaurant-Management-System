from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import re

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import RestaurantOrder
from app.models.invoicing import (
    TaxConfiguration,
    RestaurantInvoice,
    RestaurantInvoiceItem
)


invoices_bp = Blueprint("invoices", __name__)

INVOICE_ROLES = {
    "restaurant_owner",
    "general_manager",
    "assistant_manager",
    "cashier",
    "accountant",
    "system_administrator"
}

CONFIG_ROLES = {
    "restaurant_owner",
    "general_manager",
    "system_administrator"
}

CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value or 0)).quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )


def decimal_value(value, default="0"):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(default)


def get_tax_configuration():
    return db.session.get(TaxConfiguration, 1)


def configuration_response(config):
    if config is None:
        return {
            "business_name": None,
            "business_address": None,
            "gstin": None,
            "restaurant_state": None,
            "gst_rate": 5.0,
            "invoice_prefix": "INV",
            "is_gst_registered": False,
            "is_demo": True
        }

    return {
        "business_name": config.business_name,
        "business_address": config.business_address,
        "gstin": config.gstin,
        "restaurant_state": config.restaurant_state,
        "gst_rate": float(config.gst_rate),
        "invoice_prefix": config.invoice_prefix,
        "is_gst_registered": config.is_gst_registered,
        "is_demo": config.is_demo
    }


def invoice_response(invoice):
    return {
        "id": invoice.id,
        "order_id": invoice.order_id,
        "invoice_number": invoice.invoice_number,
        "invoice_date": invoice.invoice_date.isoformat(),
        "business_name": invoice.business_name,
        "business_address": invoice.business_address,
        "gstin": invoice.gstin,
        "place_of_supply_state": invoice.place_of_supply_state,
        "tax_type": invoice.tax_type,
        "taxable_value": float(invoice.taxable_value),
        "discount_amount": float(invoice.discount_amount),
        "gst_rate": float(invoice.gst_rate),
        "cgst_amount": float(invoice.cgst_amount),
        "sgst_amount": float(invoice.sgst_amount),
        "igst_amount": float(invoice.igst_amount),
        "total_tax": float(invoice.total_tax),
        "total_amount": float(invoice.total_amount),
        "is_demo": invoice.is_demo,
        "document_label": (
            "DEMO INVOICE - NOT A TAX INVOICE"
            if invoice.is_demo
            else "TAX INVOICE"
        ),
        "status": invoice.status,
        "items": [
            {
                "item_name": item.item_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "gross_amount": float(item.gross_amount),
                "discount_amount": float(item.discount_amount),
                "taxable_value": float(item.taxable_value),
                "gst_rate": float(item.gst_rate),
                "cgst_amount": float(item.cgst_amount),
                "sgst_amount": float(item.sgst_amount),
                "igst_amount": float(item.igst_amount),
                "total_amount": float(item.total_amount)
            }
            for item in invoice.items
        ]
    }


@invoices_bp.route("/gst/configuration", methods=["GET"])
@login_required
def get_gst_configuration():

    if current_user.role not in CONFIG_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to view GST settings"
        }), 403

    config = get_tax_configuration()

    return jsonify({
        "status": "success",
        "configuration": configuration_response(config)
    }), 200


@invoices_bp.route("/gst/configuration", methods=["PUT"])
@login_required
def update_gst_configuration():

    if current_user.role not in CONFIG_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to update GST settings"
        }), 403

    data = request.get_json(silent=True) or {}

    config = get_tax_configuration()

    if config is None:
        config = TaxConfiguration(id=1)
        db.session.add(config)

    if "gst_rate" in data:
        rate = decimal_value(data["gst_rate"], "-1")

        if rate < 0 or rate > 100:
            return jsonify({
                "status": "error",
                "message": "GST rate must be between 0 and 100"
            }), 400

        config.gst_rate = rate.quantize(CENT)

    if "gstin" in data:
        gstin = (data.get("gstin") or "").strip().upper()

        if gstin and not re.fullmatch(
            r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]",
            gstin
        ):
            return jsonify({
                "status": "error",
                "message": "GSTIN format is invalid"
            }), 400

        config.gstin = gstin or None

    if "business_name" in data:
        config.business_name = (
            (data.get("business_name") or "").strip() or None
        )

    if "business_address" in data:
        config.business_address = (
            (data.get("business_address") or "").strip() or None
        )

    if "restaurant_state" in data:
        config.restaurant_state = (
            (data.get("restaurant_state") or "").strip() or None
        )

    if "invoice_prefix" in data:
        prefix = (data.get("invoice_prefix") or "").strip().upper()

        if not prefix or len(prefix) > 20:
            return jsonify({
                "status": "error",
                "message": "Invoice prefix must contain 1 to 20 characters"
            }), 400

        config.invoice_prefix = prefix

    if "is_gst_registered" in data:
        if not isinstance(data["is_gst_registered"], bool):
            return jsonify({
                "status": "error",
                "message": "is_gst_registered must be true or false"
            }), 400

        config.is_gst_registered = data["is_gst_registered"]

    # Demo mode is automatically disabled only when registration
    # and a GSTIN are both provided.
    config.is_demo = not (
        config.is_gst_registered and bool(config.gstin)
    )

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "GST configuration updated successfully",
        "configuration": configuration_response(config)
    }), 200


@invoices_bp.route(
    "/invoices/orders/<int:order_id>",
    methods=["POST"]
)
@login_required
def create_invoice(order_id):

    if current_user.role not in INVOICE_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to create invoices"
        }), 403

    data = request.get_json(silent=True) or {}

    place_of_supply = (
        data.get("place_of_supply_state") or ""
    ).strip()

    if not place_of_supply:
        return jsonify({
            "status": "error",
            "message": "place_of_supply_state is required"
        }), 400

    order = db.session.get(RestaurantOrder, order_id)

    if order is None:
        return jsonify({
            "status": "error",
            "message": "Order not found"
        }), 404

    existing_invoice = RestaurantInvoice.query.filter_by(
        order_id=order.id
    ).first()

    if existing_invoice:
        return jsonify({
            "status": "error",
            "message": "An invoice already exists for this order",
            "invoice": invoice_response(existing_invoice)
        }), 409

    if not order.items:
        return jsonify({
            "status": "error",
            "message": "Cannot create an invoice for an empty order"
        }), 400

    config = get_tax_configuration()

    if config is None:
        config = TaxConfiguration(id=1)
        db.session.add(config)
        db.session.flush()

    restaurant_state = (config.restaurant_state or "").strip()

    if not restaurant_state:
        return jsonify({
            "status": "error",
            "message": "Configure the restaurant state before creating an invoice"
        }), 400

    gst_rate = money(config.gst_rate)
    subtotal = money(order.subtotal)
    discount = money(order.discount_amount)

    if discount < 0 or discount > subtotal:
        return jsonify({
            "status": "error",
            "message": "Order discount is invalid"
        }), 400

    taxable_total = money(subtotal - discount)

    if taxable_total < 0:
        return jsonify({
            "status": "error",
            "message": "Taxable value cannot be negative"
        }), 400

    same_state = (
        restaurant_state.casefold() == place_of_supply.casefold()
    )

    tax_type = "intra_state" if same_state else "inter_state"

    # Allocate the order discount proportionally across items.
    item_data = []
    allocated_discount = Decimal("0.00")

    for index, order_item in enumerate(order.items):
        gross = money(order_item.line_total)

        if index == len(order.items) - 1:
            item_discount = money(discount - allocated_discount)
        elif subtotal > 0:
            item_discount = money((gross / subtotal) * discount)
            allocated_discount += item_discount
        else:
            item_discount = Decimal("0.00")

        item_taxable = money(gross - item_discount)
        item_tax = money(item_taxable * gst_rate / Decimal("100"))

        if same_state:
            cgst = money(item_tax / Decimal("2"))
            sgst = money(item_tax - cgst)
            igst = Decimal("0.00")
        else:
            cgst = Decimal("0.00")
            sgst = Decimal("0.00")
            igst = item_tax

        item_data.append({
            "item_name": order_item.menu_item.name,
            "quantity": order_item.quantity,
            "unit_price": money(order_item.unit_price),
            "gross_amount": gross,
            "discount_amount": item_discount,
            "taxable_value": item_taxable,
            "cgst_amount": cgst,
            "sgst_amount": sgst,
            "igst_amount": igst,
            "total_amount": money(item_taxable + item_tax)
        })

    total_taxable = money(
        sum((item["taxable_value"] for item in item_data), Decimal("0"))
    )

    total_cgst = money(
        sum((item["cgst_amount"] for item in item_data), Decimal("0"))
    )

    total_sgst = money(
        sum((item["sgst_amount"] for item in item_data), Decimal("0"))
    )

    total_igst = money(
        sum((item["igst_amount"] for item in item_data), Decimal("0"))
    )

    total_tax = money(total_cgst + total_sgst + total_igst)
    total_amount = money(total_taxable + total_tax)

    # Generate a readable invoice number.
    invoice_date = datetime.utcnow()
    date_part = invoice_date.strftime("%Y%m%d")
    prefix = config.invoice_prefix or "INV"

    daily_count = RestaurantInvoice.query.filter(
        RestaurantInvoice.invoice_number.like(
            f"{prefix}-{date_part}-%"
        )
    ).count()

    invoice_number = (
        f"{prefix}-{date_part}-{daily_count + 1:04d}"
    )

    is_demo = bool(
        config.is_demo
        or not config.is_gst_registered
        or not config.gstin
    )

    invoice = RestaurantInvoice(
        order_id=order.id,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        business_name=config.business_name,
        business_address=config.business_address,
        gstin=config.gstin,
        place_of_supply_state=place_of_supply,
        tax_type=tax_type,
        taxable_value=total_taxable,
        discount_amount=discount,
        gst_rate=gst_rate,
        cgst_amount=total_cgst,
        sgst_amount=total_sgst,
        igst_amount=total_igst,
        total_tax=total_tax,
        total_amount=total_amount,
        is_demo=is_demo,
        status="issued"
    )

    db.session.add(invoice)
    db.session.flush()

    for item in item_data:
        db.session.add(
            RestaurantInvoiceItem(
                invoice_id=invoice.id,
                item_name=item["item_name"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                gross_amount=item["gross_amount"],
                discount_amount=item["discount_amount"],
                taxable_value=item["taxable_value"],
                gst_rate=gst_rate,
                cgst_amount=item["cgst_amount"],
                sgst_amount=item["sgst_amount"],
                igst_amount=item["igst_amount"],
                total_amount=item["total_amount"]
            )
        )

    # Keep the original order totals consistent with the invoice.
    order.tax_amount = total_tax
    order.total_amount = total_amount

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Invoice created successfully",
        "invoice": invoice_response(invoice)
    }), 201


@invoices_bp.route(
    "/invoices/<int:invoice_id>",
    methods=["GET"]
)
@login_required
def get_invoice(invoice_id):

    if current_user.role not in INVOICE_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to view invoices"
        }), 403

    invoice = db.session.get(RestaurantInvoice, invoice_id)

    if invoice is None:
        return jsonify({
            "status": "error",
            "message": "Invoice not found"
        }), 404

    return jsonify({
        "status": "success",
        "invoice": invoice_response(invoice)
    }), 200


@invoices_bp.route(
    "/invoices/orders/<int:order_id>",
    methods=["GET"]
)
@login_required
def get_order_invoice(order_id):

    if current_user.role not in INVOICE_ROLES:
        return jsonify({
            "status": "error",
            "message": "You do not have permission to view invoices"
        }), 403

    invoice = RestaurantInvoice.query.filter_by(
        order_id=order_id
    ).first()

    if invoice is None:
        return jsonify({
            "status": "error",
            "message": "Invoice not found for this order"
        }), 404

    return jsonify({
        "status": "success",
        "invoice": invoice_response(invoice)
    }), 200