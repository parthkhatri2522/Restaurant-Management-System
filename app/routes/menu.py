
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.extensions import db
from app.permissions import permission_required
from app.models import MenuCategory, MenuItem

menu_bp = Blueprint("menu", __name__)


# -------------------- MENU CATEGORIES --------------------

@menu_bp.route("/categories", methods=["GET"])
@login_required
@permission_required("menu.view")
def get_categories():
    categories = MenuCategory.query.order_by(MenuCategory.id).all()

    return jsonify([
        {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "is_active": category.is_active
        }
        for category in categories
    ]), 200


@menu_bp.route("/categories", methods=["POST"])
@login_required
@permission_required("menu.manage")
def create_category():
    data = request.get_json() or {}

    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    category = MenuCategory(
        name=name,
        description=data.get("description", "").strip()
    )

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "message": "Category created successfully",
        "id": category.id,
        "name": category.name
    }), 201


@menu_bp.route("/categories/<int:category_id>", methods=["PUT"])
@login_required
@permission_required("menu.manage")
def update_category(category_id):
    category = db.session.get(MenuCategory, category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Category name cannot be empty"}), 400
        category.name = name

    if "description" in data:
        category.description = data["description"].strip()

    if "is_active" in data:
        category.is_active = bool(data["is_active"])

    db.session.commit()

    return jsonify({"message": "Category updated successfully"}), 200


# -------------------- MENU ITEMS --------------------

@menu_bp.route("/menu-items", methods=["GET"])
@login_required
@permission_required("menu.view")
def get_menu_items():
    query = MenuItem.query

    category_id = request.args.get("category_id", type=int)

    if category_id:
        query = query.filter_by(category_id=category_id)

    items = query.order_by(MenuItem.id).all()

    return jsonify([
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "category_id": item.category_id,
            "is_available": item.is_available
        }
        for item in items
    ]), 200


@menu_bp.route("/menu-items", methods=["POST"])
@login_required
@permission_required("menu.manage")
def create_menu_item():
    data = request.get_json() or {}

    required_fields = ["name", "category_id", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    category = db.session.get(MenuCategory, data["category_id"])

    if not category:
        return jsonify({"error": "Category not found"}), 404

    try:
        price = float(data["price"])
        if price < 0:
            return jsonify({"error": "Price cannot be negative"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price"}), 400

    item = MenuItem(
        name=data["name"].strip(),
        description=data.get("description", "").strip(),
        price=price,
        category_id=category.id
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Menu item created successfully",
        "id": item.id,
        "name": item.name
    }), 201


@menu_bp.route("/menu-items/<int:item_id>", methods=["PUT"])
@login_required
@permission_required("menu.manage")
def update_menu_item(item_id):
    item = db.session.get(MenuItem, item_id)

    if not item:
        return jsonify({"error": "Menu item not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "Item name cannot be empty"}), 400
        item.name = name

    if "description" in data:
        item.description = data["description"].strip()

    if "price" in data:
        try:
            price = float(data["price"])
            if price < 0:
                return jsonify({"error": "Price cannot be negative"}), 400
            item.price = price
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid price"}), 400

    if "category_id" in data:
        category = db.session.get(MenuCategory, data["category_id"])
        if not category:
            return jsonify({"error": "Category not found"}), 404
        item.category_id = category.id

    if "is_available" in data:
        item.is_available = bool(data["is_available"])

    db.session.commit()

    return jsonify({"message": "Menu item updated successfully"}), 200
