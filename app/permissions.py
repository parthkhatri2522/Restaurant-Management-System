from functools import wraps
from flask import jsonify
from flask_login import current_user, login_required

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
    "system_administrator": "System Administrator",
}

DASHBOARD = frozenset({"dashboard.view"})

ROLE_PERMISSIONS = {
    "restaurant_owner": DASHBOARD | frozenset({
        "users.view", "roles.view", "employees.view", "employees.manage",
        "attendance.view", "payroll.view", "billing.view", "payments.view",
        "inventory.view", "suppliers.view", "procurement.view", "expenses.view",
        "expenses.manage", "reports.view", "quality.view", "complaints.view",
        "feedback.view", "audits.view"
    }),

    "general_manager": DASHBOARD | frozenset({
        "users.view", "employees.view", "employees.manage", "attendance.view",
        "attendance.manage", "shifts.manage", "menu.view", "menu.manage",
        "tables.view", "tables.manage", "reservations.view", "reservations.manage",
        "orders.view", "orders.manage", "kitchen.view", "billing.view",
        "inventory.view", "suppliers.view", "procurement.view", "expenses.view",
        "reports.view", "quality.view", "complaints.view", "feedback.view",
        "audits.view"
    }),

    "assistant_manager": DASHBOARD | frozenset({
        "employees.view", "attendance.view", "shifts.manage", "tables.view",
        "tables.manage", "reservations.view", "reservations.manage", "orders.view",
        "orders.manage", "kitchen.view", "quality.view", "complaints.view"
    }),

    "cashier": DASHBOARD | frozenset({
        "orders.view", "billing.view", "billing.manage", "payments.view",
        "payments.manage", "reservations.view"
    }),

    "accountant": DASHBOARD | frozenset({
        "billing.view", "payments.view", "payroll.view", "expenses.view",
        "expenses.manage", "reports.view"
    }),

    "hr_manager": DASHBOARD | frozenset({
        "employees.view", "employees.manage", "attendance.view",
        "attendance.manage", "shifts.manage", "payroll.view", "payroll.manage"
    }),

    "head_chef": DASHBOARD | frozenset({
        "menu.view", "menu.manage", "kitchen.view", "kitchen.manage",
        "inventory.view", "quality.view", "quality.manage"
    }),

    "kitchen_staff": DASHBOARD | frozenset({
        "menu.view", "kitchen.view", "kitchen.manage", "quality.view"
    }),

    "waiter": DASHBOARD | frozenset({
        "menu.view", "tables.view", "tables.manage", "reservations.view",
        "orders.view", "orders.manage", "complaints.view", "feedback.view"
    }),

    "host": DASHBOARD | frozenset({
        "tables.view", "tables.manage", "reservations.view",
        "reservations.manage", "feedback.view"
    }),

    "inventory_manager": DASHBOARD | frozenset({
        "inventory.view", "inventory.manage", "suppliers.view",
        "procurement.view", "quality.view", "reports.view"
    }),

    "procurement_manager": DASHBOARD | frozenset({
        "inventory.view", "suppliers.view", "suppliers.manage",
        "procurement.view", "procurement.manage", "expenses.view"
    }),

    "quality_officer": DASHBOARD | frozenset({
        "quality.view", "quality.manage", "complaints.view",
        "complaints.manage", "feedback.view", "audits.view"
    }),

    "housekeeping_supervisor": DASHBOARD | frozenset({
        "housekeeping.manage", "quality.view", "quality.manage", "audits.view"
    }),

    "marketing_manager": DASHBOARD | frozenset({
        "feedback.view", "marketing.manage", "reports.view"
    }),

    "system_administrator": DASHBOARD | frozenset({
        "users.view", "users.manage", "roles.view", "roles.manage",
        "settings.manage", "audits.view"
    }),
}


def has_permission(role, permission):
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def permission_required(permission):
    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapper(*args, **kwargs):
            if not has_permission(current_user.role, permission):
                return jsonify({
                    "status": "error",
                    "message": "You do not have permission to access this resource"
                }), 403

            return view_function(*args, **kwargs)

        return wrapper

    return decorator


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