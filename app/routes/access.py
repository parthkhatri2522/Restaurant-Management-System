from datetime import date

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import User, Employee
from app.permissions import ROLES, ROLE_PERMISSIONS, permission_required

access_bp = Blueprint("access", __name__)


def employee_to_dict(employee):
    return {
        "id": employee.id,
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "name": employee.full_name,
        "email": employee.email,
        "phone": employee.phone,
        "department": employee.department,
        "job_title": employee.job_title,
        "hire_date": (
            employee.hire_date.isoformat()
            if employee.hire_date else None
        ),
        "employment_status": employee.employment_status,
        "created_at": (
            employee.created_at.isoformat()
            if employee.created_at else None
        ),
    }


def employee_payload(data, employee=None):
    values = {}

    for field in ("employee_code", "first_name", "last_name"):
        value = data.get(
            field,
            getattr(employee, field, "") if employee else ""
        )

        if not isinstance(value, str) or not value.strip():
            return None, f"{field.replace('_', ' ').title()} is required."

        values[field] = value.strip()

    for field in ("email", "phone", "department", "job_title"):
        value = data.get(
            field,
            getattr(employee, field, None) if employee else None
        )

        values[field] = (
            value.strip()
            if isinstance(value, str) and value.strip()
            else None
        )

    hire_date = data.get(
        "hire_date",
        (
            employee.hire_date.isoformat()
            if employee and employee.hire_date else None
        )
    )

    if hire_date:
        try:
            values["hire_date"] = date.fromisoformat(hire_date)
        except (TypeError, ValueError):
            return None, "Hire date must use YYYY-MM-DD format."
    else:
        values["hire_date"] = None

    status = data.get(
        "employment_status",
        employee.employment_status if employee else "active"
    )

    if status not in ("active", "inactive"):
        return None, "Employment status must be active or inactive."

    values["employment_status"] = status

    return values, None


@access_bp.route("/api/roles", methods=["GET"])
@login_required
def get_roles():
    return jsonify({
        "status": "success",
        "roles": ROLES
    }), 200


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


@access_bp.route("/api/users", methods=["GET"])
@permission_required("users.view")
def get_users():
    users = User.query.order_by(User.id.asc()).all()

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


@access_bp.route("/api/employees", methods=["GET"])
@permission_required("employees.view")
def get_employees():
    query = Employee.query

    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()

    if search:
        pattern = f"%{search}%"

        query = query.filter(or_(
            Employee.employee_code.ilike(pattern),
            Employee.first_name.ilike(pattern),
            Employee.last_name.ilike(pattern),
            Employee.email.ilike(pattern),
            Employee.job_title.ilike(pattern)
        ))

    if department:
        query = query.filter(Employee.department == department)

    if status in ("active", "inactive"):
        query = query.filter(Employee.employment_status == status)

    employees = query.order_by(Employee.id.desc()).all()

    return jsonify({
        "status": "success",
        "count": len(employees),
        "employees": [
            employee_to_dict(item)
            for item in employees
        ]
    }), 200


@access_bp.route("/api/employees/<int:employee_id>", methods=["GET"])
@permission_required("employees.view")
def get_employee(employee_id):
    employee = db.session.get(Employee, employee_id)

    if employee is None:
        return jsonify({
            "status": "error",
            "message": "Employee not found."
        }), 404

    return jsonify({
        "status": "success",
        "employee": employee_to_dict(employee)
    }), 200


@access_bp.route("/api/employees", methods=["POST"])
@permission_required("employees.manage")
def create_employee():
    data = request.get_json(silent=True) or {}

    values, error = employee_payload(data)

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    duplicate = Employee.query.filter(or_(
        Employee.employee_code == values["employee_code"],
        Employee.email == values["email"] if values["email"] else False
    )).first()

    if duplicate:
        return jsonify({
            "status": "error",
            "message": "An employee with this employee code or email already exists."
        }), 409

    employee = Employee(**values)
    db.session.add(employee)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Employee code or email already exists."
        }), 409

    return jsonify({
        "status": "success",
        "message": "Employee created successfully.",
        "employee": employee_to_dict(employee)
    }), 201


@access_bp.route("/api/employees/<int:employee_id>", methods=["PUT"])
@permission_required("employees.manage")
def update_employee(employee_id):
    employee = db.session.get(Employee, employee_id)

    if employee is None:
        return jsonify({
            "status": "error",
            "message": "Employee not found."
        }), 404

    values, error = employee_payload(
        request.get_json(silent=True) or {},
        employee
    )

    if error:
        return jsonify({
            "status": "error",
            "message": error
        }), 400

    duplicate_code = Employee.query.filter(
        Employee.employee_code == values["employee_code"],
        Employee.id != employee_id
    ).first()

    duplicate_email = None

    if values["email"]:
        duplicate_email = Employee.query.filter(
            Employee.email == values["email"],
            Employee.id != employee_id
        ).first()

    if duplicate_code or duplicate_email:
        return jsonify({
            "status": "error",
            "message": "Another employee already uses this employee code or email."
        }), 409

    for field, value in values.items():
        setattr(employee, field, value)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "Employee code or email already exists."
        }), 409

    return jsonify({
        "status": "success",
        "message": "Employee updated successfully.",
        "employee": employee_to_dict(employee)
    }), 200


@access_bp.route(
    "/api/employees/<int:employee_id>/status",
    methods=["PATCH"]
)
@permission_required("employees.manage")
def update_employee_status(employee_id):
    employee = db.session.get(Employee, employee_id)

    if employee is None:
        return jsonify({
            "status": "error",
            "message": "Employee not found."
        }), 404

    status = (
        request.get_json(silent=True) or {}
    ).get("employment_status")

    if status not in ("active", "inactive"):
        return jsonify({
            "status": "error",
            "message": "Employment status must be active or inactive."
        }), 400

    employee.employment_status = status
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Employee {status} successfully.",
        "employee": employee_to_dict(employee)
    }), 200