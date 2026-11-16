from datetime import datetime

from app.extensions import db


class Employee(db.Model):

    __tablename__ = "employees"

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Employee identification
    employee_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    # Personal information
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))

    # Employment information
    department = db.Column(db.String(80))
    job_title = db.Column(db.String(80))
    hire_date = db.Column(db.Date)

    employment_status = db.Column(
        db.String(20),
        default="active",
        nullable=False
    )

    # Linked user account
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=True
    )

    # Relationship with User
    user = db.relationship(
        "User",
        back_populates="employee"
    )

    # Creation timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee {self.employee_code}>"