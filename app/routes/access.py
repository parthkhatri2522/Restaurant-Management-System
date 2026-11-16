from flask import Blueprint, jsonify

from flask_login import login_required, current_user

from app.models import User, Employee
from app.permissions import (
    ROLES,
    ROLE_PERMISSIONS,
    permission_required
)


access_bp = Blueprint("access", __name__)


# Get all available stakeholder roles
@access_bp.route("/api/roles", methods=["GET"])
@login_required
def get_roles():

    return jsonify({
        "status": "success",
        "roles": ROLES
    }), 200


# Get current user's permissions
@access_bp.route("/auth/permissions", methods=["GET"])
@login_required
def get_user_permissions():

    permissions = ROLE_PERMISSIONS.get(
        current_user.role,
        frozenset()
    )

    return jsonify({
        "status": "success",
        "username": current_user.username,
        "role": current_user.role,
        "permissions": sorted(permissions)
    }), 200


# View user accounts
@access_bp.route("/api/users", methods=["GET"])
@permission_required("users.view")
def get_users():

    users = User.query.all()

    return jsonify({
        "status": "success",
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            }
            for user in users
        ]
    }), 200


# View employee records
@access_bp.route("/api/employees", methods=["GET"])
@permission_required("employees.view")
def get_employees():

    employees = Employee.query.all()

    return jsonify({
        "status": "success",
        "employees": [
            {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "name": employee.full_name,
                "department": employee.department,
                "job_title": employee.job_title,
                "employment_status": employee.employment_status
            }
            for employee in employees
        ]
    }), 200