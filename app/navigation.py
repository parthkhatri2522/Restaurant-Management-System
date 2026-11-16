
# ServeWise - Role-Specific Sidebar Navigation

NAVIGATION_CONFIG = {

    "restaurant_owner": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "employees",
            "label": "Employees",
            "icon": "users",
            "url": "/employees",
            "permission": "employees.view"
        },
        {
            "id": "finance",
            "label": "Finance",
            "icon": "wallet",
            "url": "/finance",
            "permission": "reports.view"
        },
        {
            "id": "inventory",
            "label": "Inventory",
            "icon": "package",
            "url": "/inventory",
            "permission": "inventory.view"
        },
        {
            "id": "quality",
            "label": "Quality Management",
            "icon": "shield-check",
            "url": "/quality",
            "permission": "quality.view"
        },
        {
            "id": "reports",
            "label": "Reports",
            "icon": "chart-no-axes-combined",
            "url": "/reports",
            "permission": "reports.view"
        }
    ],

    "general_manager": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "orders",
            "label": "Orders",
            "icon": "shopping-bag",
            "url": "/orders",
            "permission": "orders.view"
        },
        {
            "id": "reservations",
            "label": "Reservations",
            "icon": "calendar-days",
            "url": "/reservations",
            "permission": "reservations.view"
        },
        {
            "id": "employees",
            "label": "Employees",
            "icon": "users",
            "url": "/employees",
            "permission": "employees.view"
        },
        {
            "id": "inventory",
            "label": "Inventory",
            "icon": "package",
            "url": "/inventory",
            "permission": "inventory.view"
        },
        {
            "id": "reports",
            "label": "Reports",
            "icon": "chart-no-axes-combined",
            "url": "/reports",
            "permission": "reports.view"
        }
    ],

    "assistant_manager": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "shifts",
            "label": "Shift Management",
            "icon": "calendar-clock",
            "url": "/shifts",
            "permission": "shifts.manage"
        },
        {
            "id": "employees",
            "label": "Employees",
            "icon": "users",
            "url": "/employees",
            "permission": "employees.view"
        },
        {
            "id": "tables",
            "label": "Tables",
            "icon": "armchair",
            "url": "/tables",
            "permission": "tables.view"
        },
        {
            "id": "orders",
            "label": "Orders",
            "icon": "shopping-bag",
            "url": "/orders",
            "permission": "orders.view"
        },
        {
            "id": "complaints",
            "label": "Complaints",
            "icon": "message-square-warning",
            "url": "/complaints",
            "permission": "complaints.view"
        }
    ],

    "cashier": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "billing",
            "label": "Billing",
            "icon": "receipt",
            "url": "/billing",
            "permission": "billing.view"
        },
        {
            "id": "payments",
            "label": "Payments",
            "icon": "credit-card",
            "url": "/payments",
            "permission": "payments.view"
        },
        {
            "id": "orders",
            "label": "Orders",
            "icon": "shopping-bag",
            "url": "/orders",
            "permission": "orders.view"
        }
    ],

    "accountant": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "revenue",
            "label": "Revenue",
            "icon": "trending-up",
            "url": "/revenue",
            "permission": "reports.view"
        },
        {
            "id": "expenses",
            "label": "Expenses",
            "icon": "wallet",
            "url": "/expenses",
            "permission": "expenses.view"
        },
        {
            "id": "payroll",
            "label": "Payroll",
            "icon": "banknote",
            "url": "/payroll",
            "permission": "payroll.view"
        },
        {
            "id": "reports",
            "label": "Financial Reports",
            "icon": "chart-no-axes-combined",
            "url": "/reports",
            "permission": "reports.view"
        }
    ],

    "hr_manager": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "employees",
            "label": "Employees",
            "icon": "users",
            "url": "/employees",
            "permission": "employees.view"
        },
        {
            "id": "attendance",
            "label": "Attendance",
            "icon": "clipboard-check",
            "url": "/attendance",
            "permission": "attendance.view"
        },
        {
            "id": "shifts",
            "label": "Shift Scheduling",
            "icon": "calendar-clock",
            "url": "/shifts",
            "permission": "shifts.manage"
        },
        {
            "id": "payroll",
            "label": "Payroll",
            "icon": "banknote",
            "url": "/payroll",
            "permission": "payroll.view"
        }
    ],

    "head_chef": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "kitchen",
            "label": "Kitchen Orders",
            "icon": "chef-hat",
            "url": "/kitchen",
            "permission": "kitchen.view"
        },
        {
            "id": "menu",
            "label": "Menu Management",
            "icon": "utensils",
            "url": "/menu",
            "permission": "menu.manage"
        },
        {
            "id": "inventory",
            "label": "Ingredients",
            "icon": "package",
            "url": "/inventory",
            "permission": "inventory.view"
        },
        {
            "id": "quality",
            "label": "Food Quality",
            "icon": "shield-check",
            "url": "/quality",
            "permission": "quality.view"
        }
    ],

    "kitchen_staff": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "kitchen",
            "label": "Kitchen Orders",
            "icon": "chef-hat",
            "url": "/kitchen",
            "permission": "kitchen.view"
        },
        {
            "id": "menu",
            "label": "Menu Reference",
            "icon": "utensils",
            "url": "/menu",
            "permission": "menu.view"
        },
        {
            "id": "quality",
            "label": "Food Safety",
            "icon": "shield-check",
            "url": "/quality",
            "permission": "quality.view"
        }
    ],

    "waiter": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "tables",
            "label": "Tables",
            "icon": "armchair",
            "url": "/tables",
            "permission": "tables.view"
        },
        {
            "id": "orders",
            "label": "Customer Orders",
            "icon": "shopping-bag",
            "url": "/orders",
            "permission": "orders.view"
        },
        {
            "id": "reservations",
            "label": "Reservations",
            "icon": "calendar-days",
            "url": "/reservations",
            "permission": "reservations.view"
        },
        {
            "id": "feedback",
            "label": "Customer Feedback",
            "icon": "message-square",
            "url": "/feedback",
            "permission": "feedback.view"
        }
    ],

    "host": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "reservations",
            "label": "Reservations",
            "icon": "calendar-days",
            "url": "/reservations",
            "permission": "reservations.manage"
        },
        {
            "id": "tables",
            "label": "Table Availability",
            "icon": "armchair",
            "url": "/tables",
            "permission": "tables.view"
        },
        {
            "id": "feedback",
            "label": "Customer Feedback",
            "icon": "message-square",
            "url": "/feedback",
            "permission": "feedback.view"
        }
    ],

    "inventory_manager": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "inventory",
            "label": "Stock Management",
            "icon": "package",
            "url": "/inventory",
            "permission": "inventory.manage"
        },
        {
            "id": "expiry",
            "label": "Expiry Tracking",
            "icon": "calendar-clock",
            "url": "/inventory/expiry",
            "permission": "inventory.manage"
        },
        {
            "id": "wastage",
            "label": "Wastage Tracking",
            "icon": "trash-2",
            "url": "/inventory/wastage",
            "permission": "inventory.manage"
        },
        {
            "id": "suppliers",
            "label": "Suppliers",
            "icon": "truck",
            "url": "/suppliers",
            "permission": "suppliers.view"
        }
    ],

    "procurement_manager": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "suppliers",
            "label": "Suppliers",
            "icon": "truck",
            "url": "/suppliers",
            "permission": "suppliers.manage"
        },
        {
            "id": "procurement",
            "label": "Purchase Orders",
            "icon": "shopping-cart",
            "url": "/procurement",
            "permission": "procurement.manage"
        },
        {
            "id": "inventory",
            "label": "Inventory",
            "icon": "package",
            "url": "/inventory",
            "permission": "inventory.view"
        },
        {
            "id": "expenses",
            "label": "Expenses",
            "icon": "wallet",
            "url": "/expenses",
            "permission": "expenses.view"
        }
    ],

    "quality_officer": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "quality",
            "label": "Quality Checklists",
            "icon": "shield-check",
            "url": "/quality",
            "permission": "quality.manage"
        },
        {
            "id": "complaints",
            "label": "Complaints",
            "icon": "message-square-warning",
            "url": "/complaints",
            "permission": "complaints.manage"
        },
        {
            "id": "feedback",
            "label": "Customer Feedback",
            "icon": "message-square",
            "url": "/feedback",
            "permission": "feedback.view"
        },
        {
            "id": "audits",
            "label": "Quality Audits",
            "icon": "clipboard-check",
            "url": "/audits",
            "permission": "audits.view"
        }
    ],

    "housekeeping_supervisor": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "housekeeping",
            "label": "Cleaning Activities",
            "icon": "spray-can",
            "url": "/housekeeping",
            "permission": "housekeeping.manage"
        },
        {
            "id": "quality",
            "label": "Hygiene Inspections",
            "icon": "shield-check",
            "url": "/quality",
            "permission": "quality.manage"
        },
        {
            "id": "audits",
            "label": "Inspection Records",
            "icon": "clipboard-check",
            "url": "/audits",
            "permission": "audits.view"
        }
    ],

    "marketing_manager": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "feedback",
            "label": "Customer Feedback",
            "icon": "message-square",
            "url": "/feedback",
            "permission": "feedback.view"
        },
        {
            "id": "marketing",
            "label": "Marketing Campaigns",
            "icon": "megaphone",
            "url": "/marketing",
            "permission": "marketing.manage"
        },
        {
            "id": "reports",
            "label": "Performance Reports",
            "icon": "chart-no-axes-combined",
            "url": "/reports",
            "permission": "reports.view"
        }
    ],

    "system_administrator": [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "icon": "layout-dashboard",
            "url": "/dashboard",
            "permission": "dashboard.view"
        },
        {
            "id": "users",
            "label": "User Accounts",
            "icon": "users",
            "url": "/users",
            "permission": "users.view"
        },
        {
            "id": "roles",
            "label": "Role Management",
            "icon": "shield",
            "url": "/roles",
            "permission": "roles.view"
        },
        {
            "id": "settings",
            "label": "System Settings",
            "icon": "settings",
            "url": "/settings",
            "permission": "settings.manage"
        },
        {
            "id": "audits",
            "label": "Activity Logs",
            "icon": "clipboard-list",
            "url": "/audits",
            "permission": "audits.view"
        }
    ]
}
