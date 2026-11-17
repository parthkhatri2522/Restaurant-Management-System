
from datetime import datetime

from app.extensions import db


class MenuCategory(db.Model):
    __tablename__ = "menu_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    menu_items = db.relationship(
        "MenuItem",
        back_populates="category",
        lazy=True
    )

    def __repr__(self):
        return f"<MenuCategory {self.name}>"


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_categories.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    price = db.Column(db.Numeric(10, 2), nullable=False)

    preparation_time = db.Column(
        db.Integer,
        default=15,
        nullable=False
    )

    is_available = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    category = db.relationship(
        "MenuCategory",
        back_populates="menu_items"
    )

    order_items = db.relationship(
        "OrderItem",
        back_populates="menu_item",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "price >= 0",
            name="check_menu_item_price"
        ),
        db.CheckConstraint(
            "preparation_time >= 0",
            name="check_preparation_time"
        ),
        db.Index("idx_menu_item_category", "category_id"),
    )

    def __repr__(self):
        return f"<MenuItem {self.name}>"


class RestaurantTable(db.Model):
    __tablename__ = "restaurant_tables"

    id = db.Column(db.Integer, primary_key=True)

    table_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    capacity = db.Column(db.Integer, nullable=False)

    status = db.Column(
        db.String(30),
        default="available",
        nullable=False
    )

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    reservations = db.relationship(
        "Reservation",
        back_populates="restaurant_table",
        lazy=True
    )

    orders = db.relationship(
        "RestaurantOrder",
        back_populates="restaurant_table",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "capacity > 0",
            name="check_table_capacity"
        ),
        db.CheckConstraint(
            "status IN ('available', 'occupied', 'reserved', 'maintenance')",
            name="check_table_status"
        ),
    )

    def __repr__(self):
        return f"<RestaurantTable {self.table_number}>"


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(120),
        nullable=False
    )

    customer_phone = db.Column(
        db.String(20),
        nullable=False
    )

    customer_email = db.Column(db.String(120))

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_tables.id"),
        nullable=True
    )

    party_size = db.Column(db.Integer, nullable=False)

    reservation_time = db.Column(
        db.DateTime,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    special_requests = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    restaurant_table = db.relationship(
        "RestaurantTable",
        back_populates="reservations"
    )

    orders = db.relationship(
        "RestaurantOrder",
        back_populates="reservation",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "party_size > 0",
            name="check_reservation_party_size"
        ),
        db.CheckConstraint(
            "status IN ('pending', 'confirmed', 'seated', 'completed', 'cancelled')",
            name="check_reservation_status"
        ),
        db.Index("idx_reservation_time", "reservation_time"),
    )

    def __repr__(self):
        return f"<Reservation {self.customer_name}>"


class RestaurantOrder(db.Model):
    __tablename__ = "restaurant_orders"

    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )

    customer_name = db.Column(db.String(120))

    order_type = db.Column(
        db.String(30),
        default="dine_in",
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    table_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_tables.id"),
        nullable=True
    )

    reservation_id = db.Column(
        db.Integer,
        db.ForeignKey("reservations.id"),
        nullable=True
    )

    subtotal = db.Column(
        db.Numeric(10, 2),
        default=0,
        nullable=False
    )

    tax_amount = db.Column(
        db.Numeric(10, 2),
        default=0,
        nullable=False
    )

    discount_amount = db.Column(
        db.Numeric(10, 2),
        default=0,
        nullable=False
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        default=0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    restaurant_table = db.relationship(
        "RestaurantTable",
        back_populates="orders"
    )

    reservation = db.relationship(
        "Reservation",
        back_populates="orders"
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy=True
    )

    payments = db.relationship(
        "Payment",
        back_populates="order",
        lazy=True
    )

    __table_args__ = (
        db.CheckConstraint(
            "subtotal >= 0 AND tax_amount >= 0 "
            "AND discount_amount >= 0 AND total_amount >= 0",
            name="check_order_amounts"
        ),
        db.CheckConstraint(
            "order_type IN ('dine_in', 'takeaway', 'delivery')",
            name="check_order_type"
        ),
        db.CheckConstraint(
            "status IN ('pending', 'confirmed', 'preparing', "
            "'ready', 'served', 'completed', 'cancelled')",
            name="check_order_status"
        ),
        db.Index("idx_order_status", "status"),
        db.Index("idx_order_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<RestaurantOrder {self.order_number}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_orders.id", ondelete="CASCADE"),
        nullable=False
    )

    menu_item_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_items.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)

    unit_price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    line_total = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    special_instructions = db.Column(db.Text)

    order = db.relationship(
        "RestaurantOrder",
        back_populates="items"
    )

    menu_item = db.relationship(
        "MenuItem",
        back_populates="order_items"
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="check_order_item_quantity"
        ),
        db.CheckConstraint(
            "unit_price >= 0 AND line_total >= 0",
            name="check_order_item_price"
        ),
    )

    def __repr__(self):
        return f"<OrderItem {self.id}>"


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("restaurant_orders.id"),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    payment_method = db.Column(
        db.String(30),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    transaction_reference = db.Column(
        db.String(120),
        unique=True
    )

    paid_at = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    order = db.relationship(
        "RestaurantOrder",
        back_populates="payments"
    )

    __table_args__ = (
        db.CheckConstraint(
            "amount >= 0",
            name="check_payment_amount"
        ),
        db.CheckConstraint(
            "payment_method IN ('cash', 'card', 'upi', 'online')",
            name="check_payment_method"
        ),
        db.CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'refunded')",
            name="check_payment_status"
        ),
        db.Index("idx_payment_order", "order_id"),
    )

    def __repr__(self):
        return f"<Payment {self.id}>"
