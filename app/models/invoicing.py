from datetime import datetime

from app.extensions import db


class TaxConfiguration(db.Model):
    __tablename__ = "restaurant_tax_settings"

    id = db.Column(db.Integer, primary_key=True)

    business_name = db.Column(db.String(150), nullable=True)
    business_address = db.Column(db.Text, nullable=True)
    gstin = db.Column(db.String(15), nullable=True)
    restaurant_state = db.Column(db.String(100), nullable=True)

    gst_rate = db.Column(
        db.Numeric(5, 2),
        nullable=False,
        default=5.00
    )

    invoice_prefix = db.Column(
        db.String(20),
        nullable=False,
        default="INV"
    )

    is_gst_registered = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    is_demo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class RestaurantInvoice(db.Model):
    __tablename__ = "restaurant_invoices"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_orders.id"),
        nullable=False,
        unique=True
    )

    invoice_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    invoice_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    business_name = db.Column(db.String(150), nullable=True)
    business_address = db.Column(db.Text, nullable=True)
    gstin = db.Column(db.String(15), nullable=True)

    place_of_supply_state = db.Column(
        db.String(100),
        nullable=False
    )

    tax_type = db.Column(
        db.String(20),
        nullable=False
    )

    taxable_value = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    discount_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    gst_rate = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )

    cgst_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    sgst_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    igst_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    total_tax = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    is_demo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="issued"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    items = db.relationship(
        "RestaurantInvoiceItem",
        backref="invoice",
        lazy=True,
        cascade="all, delete-orphan"
    )


class RestaurantInvoiceItem(db.Model):
    __tablename__ = "restaurant_invoice_items"

    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_invoices.id"),
        nullable=False
    )

    item_name = db.Column(
        db.String(150),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    gross_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    discount_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    taxable_value = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    gst_rate = db.Column(
        db.Numeric(5, 2),
        nullable=False
    )

    cgst_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    sgst_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    igst_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )