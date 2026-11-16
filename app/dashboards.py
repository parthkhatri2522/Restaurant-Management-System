
# ServeWise - Stakeholder Dashboard Configurations

DASHBOARD_CONFIG = {

    "restaurant_owner": {
        "title": "Owner Dashboard",
        "description": "Overall restaurant business performance",
        "widgets": [
            {
                "id": "revenue",
                "title": "Revenue Overview",
                "description": "Monitor restaurant revenue",
                "data_source": "sales"
            },
            {
                "id": "expenses",
                "title": "Business Expenses",
                "description": "Monitor operational expenses",
                "data_source": "expenses"
            },
            {
                "id": "profit",
                "title": "Profit Overview",
                "description": "Review business profitability",
                "data_source": "financial_reports"
            },
            {
                "id": "quality",
                "title": "Quality Performance",
                "description": "Monitor restaurant quality standards",
                "data_source": "quality"
            }
        ]
    },

    "general_manager": {
        "title": "General Manager Dashboard",
        "description": "Monitor daily restaurant operations",
        "widgets": [
            {
                "id": "orders",
                "title": "Order Overview",
                "description": "Monitor restaurant orders",
                "data_source": "orders"
            },
            {
                "id": "employees",
                "title": "Employee Overview",
                "description": "Monitor employee information",
                "data_source": "employees"
            },
            {
                "id": "reservations",
                "title": "Reservations",
                "description": "Monitor customer reservations",
                "data_source": "reservations"
            },
            {
                "id": "operations",
                "title": "Operational Performance",
                "description": "Review daily operations",
                "data_source": "operations"
            }
        ]
    },

    "assistant_manager": {
        "title": "Assistant Manager Dashboard",
        "description": "Manage daily shifts and restaurant activities",
        "widgets": [
            {
                "id": "shifts",
                "title": "Shift Overview",
                "description": "Monitor ongoing shifts",
                "data_source": "shifts"
            },
            {
                "id": "staff",
                "title": "Staff Overview",
                "description": "Monitor shift staff",
                "data_source": "employees"
            },
            {
                "id": "tables",
                "title": "Table Status",
                "description": "Monitor restaurant tables",
                "data_source": "tables"
            },
            {
                "id": "complaints",
                "title": "Customer Complaints",
                "description": "Review customer complaints",
                "data_source": "complaints"
            }
        ]
    },

    "cashier": {
        "title": "Cashier Dashboard",
        "description": "Manage billing and payment activities",
        "widgets": [
            {
                "id": "billing",
                "title": "Billing Overview",
                "description": "Access customer billing",
                "data_source": "billing"
            },
            {
                "id": "payments",
                "title": "Payment Records",
                "description": "Monitor payment transactions",
                "data_source": "payments"
            },
            {
                "id": "orders",
                "title": "Active Orders",
                "description": "View orders awaiting billing",
                "data_source": "orders"
            }
        ]
    },

    "accountant": {
        "title": "Accountant Dashboard",
        "description": "Monitor financial records and reports",
        "widgets": [
            {
                "id": "revenue",
                "title": "Revenue Records",
                "description": "Review restaurant revenue",
                "data_source": "sales"
            },
            {
                "id": "expenses",
                "title": "Expense Records",
                "description": "Review business expenses",
                "data_source": "expenses"
            },
            {
                "id": "payroll",
                "title": "Payroll Overview",
                "description": "Review payroll information",
                "data_source": "payroll"
            },
            {
                "id": "reports",
                "title": "Financial Reports",
                "description": "Access financial reports",
                "data_source": "financial_reports"
            }
        ]
    },

    "hr_manager": {
        "title": "HR Manager Dashboard",
        "description": "Manage employee and human resource activities",
        "widgets": [
            {
                "id": "employees",
                "title": "Employee Records",
                "description": "Monitor employee information",
                "data_source": "employees"
            },
            {
                "id": "attendance",
                "title": "Attendance Overview",
                "description": "Monitor employee attendance",
                "data_source": "attendance"
            },
            {
                "id": "shifts",
                "title": "Shift Scheduling",
                "description": "Review employee shifts",
                "data_source": "shifts"
            },
            {
                "id": "payroll",
                "title": "Payroll Overview",
                "description": "Monitor employee payroll",
                "data_source": "payroll"
            }
        ]
    },

    "head_chef": {
        "title": "Head Chef Dashboard",
        "description": "Manage kitchen operations and food quality",
        "widgets": [
            {
                "id": "kitchen",
                "title": "Kitchen Orders",
                "description": "Monitor kitchen order preparation",
                "data_source": "kitchen"
            },
            {
                "id": "menu",
                "title": "Menu Management",
                "description": "Manage restaurant menu items",
                "data_source": "menu"
            },
            {
                "id": "inventory",
                "title": "Ingredient Inventory",
                "description": "Monitor kitchen ingredients",
                "data_source": "inventory"
            },
            {
                "id": "quality",
                "title": "Food Quality",
                "description": "Monitor food safety standards",
                "data_source": "quality"
            }
        ]
    },

    "kitchen_staff": {
        "title": "Kitchen Staff Dashboard",
        "description": "View and manage kitchen preparation activities",
        "widgets": [
            {
                "id": "kitchen_orders",
                "title": "Assigned Kitchen Orders",
                "description": "View orders requiring preparation",
                "data_source": "kitchen"
            },
            {
                "id": "menu",
                "title": "Menu Reference",
                "description": "View restaurant menu items",
                "data_source": "menu"
            },
            {
                "id": "quality",
                "title": "Food Safety Checklist",
                "description": "Review food safety requirements",
                "data_source": "quality"
            }
        ]
    },

    "waiter": {
        "title": "Waiter Dashboard",
        "description": "Manage customer orders and table service",
        "widgets": [
            {
                "id": "tables",
                "title": "Table Overview",
                "description": "Monitor assigned tables",
                "data_source": "tables"
            },
            {
                "id": "orders",
                "title": "Customer Orders",
                "description": "Manage customer orders",
                "data_source": "orders"
            },
            {
                "id": "reservations",
                "title": "Reservations",
                "description": "View customer reservations",
                "data_source": "reservations"
            },
            {
                "id": "feedback",
                "title": "Customer Feedback",
                "description": "Review customer feedback",
                "data_source": "feedback"
            }
        ]
    },

    "host": {
        "title": "Host Dashboard",
        "description": "Manage reservations and customer seating",
        "widgets": [
            {
                "id": "reservations",
                "title": "Reservation Overview",
                "description": "Manage customer reservations",
                "data_source": "reservations"
            },
            {
                "id": "tables",
                "title": "Table Availability",
                "description": "Monitor table availability",
                "data_source": "tables"
            },
            {
                "id": "feedback",
                "title": "Customer Feedback",
                "description": "Review customer feedback",
                "data_source": "feedback"
            }
        ]
    },

    "inventory_manager": {
        "title": "Inventory Manager Dashboard",
        "description": "Monitor stock and inventory operations",
        "widgets": [
            {
                "id": "stock",
                "title": "Stock Overview",
                "description": "Monitor available stock",
                "data_source": "inventory"
            },
            {
                "id": "expiry",
                "title": "Expiry Monitoring",
                "description": "Monitor expiring inventory",
                "data_source": "inventory_expiry"
            },
            {
                "id": "wastage",
                "title": "Wastage Records",
                "description": "Monitor stock wastage",
                "data_source": "inventory_wastage"
            },
            {
                "id": "suppliers",
                "title": "Supplier Overview",
                "description": "Review supplier information",
                "data_source": "suppliers"
            }
        ]
    },

    "procurement_manager": {
        "title": "Procurement Manager Dashboard",
        "description": "Manage suppliers and purchasing activities",
        "widgets": [
            {
                "id": "suppliers",
                "title": "Supplier Records",
                "description": "Monitor supplier information",
                "data_source": "suppliers"
            },
            {
                "id": "purchase_orders",
                "title": "Purchase Orders",
                "description": "Manage purchasing activities",
                "data_source": "procurement"
            },
            {
                "id": "inventory",
                "title": "Stock Requirements",
                "description": "Review inventory requirements",
                "data_source": "inventory"
            },
            {
                "id": "expenses",
                "title": "Procurement Expenses",
                "description": "Monitor purchasing expenses",
                "data_source": "expenses"
            }
        ]
    },

    "quality_officer": {
        "title": "Quality Officer Dashboard",
        "description": "Monitor food safety and quality standards",
        "widgets": [
            {
                "id": "quality",
                "title": "Quality Checklists",
                "description": "Monitor quality inspections",
                "data_source": "quality"
            },
            {
                "id": "complaints",
                "title": "Complaint Records",
                "description": "Monitor quality-related complaints",
                "data_source": "complaints"
            },
            {
                "id": "feedback",
                "title": "Customer Feedback",
                "description": "Review quality feedback",
                "data_source": "feedback"
            },
            {
                "id": "audits",
                "title": "Audit Overview",
                "description": "Monitor quality audits",
                "data_source": "audits"
            }
        ]
    },

    "housekeeping_supervisor": {
        "title": "Housekeeping Dashboard",
        "description": "Monitor hygiene and housekeeping activities",
        "widgets": [
            {
                "id": "housekeeping",
                "title": "Cleaning Activities",
                "description": "Monitor cleaning operations",
                "data_source": "housekeeping"
            },
            {
                "id": "quality",
                "title": "Hygiene Inspections",
                "description": "Review hygiene checklists",
                "data_source": "quality"
            },
            {
                "id": "audits",
                "title": "Inspection Records",
                "description": "Review inspection records",
                "data_source": "audits"
            }
        ]
    },

    "marketing_manager": {
        "title": "Marketing Manager Dashboard",
        "description": "Monitor customer feedback and marketing performance",
        "widgets": [
            {
                "id": "feedback",
                "title": "Customer Feedback",
                "description": "Monitor customer feedback",
                "data_source": "feedback"
            },
            {
                "id": "campaigns",
                "title": "Marketing Campaigns",
                "description": "Manage marketing activities",
                "data_source": "marketing"
            },
            {
                "id": "reports",
                "title": "Performance Reports",
                "description": "Review marketing performance",
                "data_source": "reports"
            }
        ]
    },

    "system_administrator": {
        "title": "System Administrator Dashboard",
        "description": "Manage system accounts and technical settings",
        "widgets": [
            {
                "id": "users",
                "title": "User Accounts",
                "description": "Monitor system user accounts",
                "data_source": "users"
            },
            {
                "id": "roles",
                "title": "Role Management",
                "description": "Review stakeholder roles",
                "data_source": "roles"
            },
            {
                "id": "system",
                "title": "System Configuration",
                "description": "Manage technical system settings",
                "data_source": "settings"
            },
            {
                "id": "audits",
                "title": "System Activity",
                "description": "Review system activity records",
                "data_source": "audits"
            }
        ]
    }
}
