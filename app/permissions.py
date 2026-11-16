from functools import wraps

from flask import jsonify
from flask_login import current_user, login_required


# All stakeholder roles in ServeWise
ROLES = {
    "restaurant_owner": "Restaurant Owner",
    "general_manager": "General Manager",
    "assistant_manager": "Assistant / Shift Manager",
    "cashier": "Cashier",
    "accountant": "Accountant",
    "hr_manager": "HR Manager",
    "head_chef": "Head Chef",
    "kitchen_staff": "Kitchen Staff",
    "waiter": "Waiter / Server",
    "host": "Host / Receptionist",
    "inventory_manager": "Inventory Manager",
    "procurement_manager": "Procurement Manager",
    "quality_officer": "Quality / Food Safety Officer",
    "housekeeping_supervisor": "Housekeeping Supervisor",
    "marketing_manager": "Marketing Manager",
    "system_administrator": "System Administrator"
}


# Common dashboard permission
DASHBOARD = frozenset({
    "dashboard.view"
})


# Role-wise permission definitions
ROLE_PERMISSIONS = {

    # Restaurant Owner
    "restaurant_owner": DASHBOARD | frozenset({
        "users.view",
        "roles.view",
        "employees.view",
        "attendance.view",
        "payroll.view",
        "billing.view",
        "payments.view",
        "inventory.view",
        "suppliers.view",
        "procurement.view",
        "expenses.view",
        "expenses.manage",
        "reports.view",
        "quality.view",
        "complaints.view",
        "feedback.view",
        "audits.view"
    }),

    # General Manager
    "general_manager": DASHBOARD | frozenset({
        "users.view",
        "employees.view",
        "employees.manage",
        "attendance.view",
        "attendance.manage",
        "shifts.manage",
        "menu.view",
        "menu.manage",
        "tables.view",
        "tables.manage",
        "reservations.view",
        "reservations.manage",
        "orders.view",
        "orders.manage",
        "kitchen.view",
        "billing.view",
        "inventory.view",
        "suppliers.view",
        "procurement.view",
        "expenses.view",
        "reports.view",
        "quality.view",
        "complaints.view",
        "feedback.view",
        "audits.view"
    }),

    # Assistant / Shift Manager
    "assistant_manager": DASHBOARD | frozenset({
        "employees.view",
        "attendance.view",
        "shifts.manage",
        "tables.view",
        "tables.manage",
        "reservations.view",
        "reservations.manage",
        "orders.view",
        "orders.manage",
        "kitchen.view",
        "quality.view",
        "complaints.view"
    }),

    # Cashier
    "cashier": DASHBOARD | frozenset({
        "orders.view",
        "billing.view",
        "billing.manage",
        "payments.view",
        "payments.manage",
        "reservations.view"
    }),

    # Accountant
    "accountant": DASHBOARD | frozenset({
        "billing.view",
        "payments.view",
        "payroll.view",
        "expenses.view",
        "expenses.manage",
        "reports.view"
    }),

    # HR Manager
    "hr_manager": DASHBOARD | frozenset({
        "employees.view",
        "employees.manage",
        "attendance.view",
        "attendance.manage",
        "shifts.manage",
        "payroll.view",
        "payroll.manage"
    }),

    # Head Chef
    "head_chef": DASHBOARD | frozenset({
        "menu.view",
        "menu.manage",
        "kitchen.view",
        "kitchen.manage",
        "inventory.view",
        "quality.view",
        "quality.manage"
    }),

    # Kitchen Staff
    "kitchen_staff": DASHBOARD | frozenset({
        "menu.view",
        "kitchen.view",
        "kitchen.manage",
        "quality.view"
    }),

    # Waiter / Server
    "waiter": DASHBOARD | frozenset({
        "menu.view",
        "tables.view",
        "tables.manage",
        "reservations.view",
        "orders.view",
        "orders.manage",
        "complaints.view",
        "feedback.view"
    }),

    # Host / Receptionist
    "host": DASHBOARD | frozenset({
        "tables.view",
        "tables.manage",
        "reservations.view",
        "reservations.manage",
        "feedback.view"
    }),

    # Inventory Manager
    "inventory_manager": DASHBOARD | frozenset({
        "inventory.view",
        "inventory.manage",
        "suppliers.view",
        "procurement.view",
        "quality.view",
        "reports.view"
    }),

    # Procurement Manager
    "procurement_manager": DASHBOARD | frozenset({
        "inventory.view",
        "suppliers.view",
        "suppliers.manage",
        "procurement.view",
        "procurement.manage",
        "expenses.view"
    }),

    # Quality / Food Safety Officer
    "quality_officer": DASHBOARD | frozenset({
        "quality.view",
        "quality.manage",
        "complaints.view",
        "complaints.manage",
        "feedback.view",
        "audits.view"
    }),

    # Housekeeping Supervisor
    "housekeeping_supervisor": DASHBOARD | frozenset({
        "housekeeping.manage",
        "quality.view",
        "quality.manage",
        "audits.view"
    }),

    # Marketing Manager
    "marketing_manager": DASHBOARD | frozenset({
        "feedback.view",
        "marketing.manage",
        "reports.view"
    }),

    # System Administrator
    "system_administrator": DASHBOARD | frozenset({
        "users.view",
        "users.manage",
        "roles.view",
        "roles.manage",
        "settings.manage",
        "audits.view"
    })
}


# Check whether a role has a particular permission
def has_permission(role, permission):

    permissions = ROLE_PERMISSIONS.get(role, frozenset())

    return permission in permissions


# Decorator for permission-based access
def permission_required(permission):

    def decorator(view_function):

        @wraps(view_function)
        @login_required
        def wrapper(*args, **kwargs):

            if not has_permission(
                current_user.role,
                permission
            ):

                return jsonify({
                    "status": "error",
                    "message": "You do not have permission to access this resource"
                }), 403

            return view_function(*args, **kwargs)

        return wrapper

    return decorator


# Decorator for role-based access
def role_required(*allowed_roles):

    def decorator(view_function):

        @wraps(view_function)
        @login_required
        def wrapper(*args, **kwargs):

            if current_user.role not in allowed_roles:

                return jsonify({
                    "status": "error",
                    "message": "Access denied for your role"
                }), 403

            return view_function(*args, **kwargs)

        return wrapper

    return decorator