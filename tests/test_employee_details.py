import unittest

from app import create_app
from app.extensions import db
from app.models import User


class EmployeeDetailsTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://"
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            owner = User(
                username="detailsowner",
                email="detailsowner@example.com",
                role="restaurant_owner",
                is_active=True
            )
            owner.set_password("testpassword123")
            db.session.add(owner)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        return self.client.post(
            "/auth/login",
            json={
                "username": "detailsowner",
                "password": "testpassword123"
            }
        )

    def create_employee(self):
        return self.client.post(
            "/api/employees",
            json={
                "employee_code": "EMP-DETAIL-01",
                "first_name": "Aarav",
                "last_name": "Sharma",
                "email": "aarav.details@example.com",
                "phone": "9876543210",
                "department": "Kitchen",
                "job_title": "Head Chef",
                "hire_date": "2026-01-15",
                "employment_status": "active"
            }
        )

    def test_owner_can_view_employee_details(self):
        self.login()
        created = self.create_employee()

        self.assertEqual(created.status_code, 201)
        employee_id = created.get_json()["employee"]["id"]

        response = self.client.get(
            f"/api/employees/{employee_id}"
        )

        self.assertEqual(response.status_code, 200)

        employee = response.get_json()["employee"]
        self.assertEqual(employee["name"], "Aarav Sharma")
        self.assertEqual(employee["employee_code"], "EMP-DETAIL-01")
        self.assertEqual(employee["department"], "Kitchen")
        self.assertEqual(employee["job_title"], "Head Chef")

    def test_missing_employee_details_returns_404(self):
        self.login()

        response = self.client.get("/api/employees/999999")

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()