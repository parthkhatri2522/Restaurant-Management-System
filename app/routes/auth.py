from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User


auth_bp = Blueprint("auth", __name__)


# User login
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password are required"
        }), 400

    user = User.query.filter_by(username=username).first()

    if user is None or not user.check_password(password):
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401

    if not user.is_active:
        return jsonify({
            "status": "error",
            "message": "This account is inactive"
        }), 403

    login_user(user)

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200


# User logout
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    return jsonify({
        "status": "success",
        "message": "Logout successful"
    }), 200


# Get currently authenticated user
@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user():

    return jsonify({
        "status": "success",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }), 200