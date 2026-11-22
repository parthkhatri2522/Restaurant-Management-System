import unittest

from app import create_app
from app.extensions import db
from app.models import User


class EmployeeTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app()

        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://"
        })

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            for username, role in [
                ("employeeowner", "restaurant_owner"),
                ("employeeassistant", "assistant_manager")
            ]:
                user = User(
                    username=username,
                    email=f"{username}@example.com",
                    role=role,
                    is_active=True
                )

                user.set_password("testpassword123")
                db.session.add(user)

            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username):
        return self.client.post(
            "/auth/login",
            json={
                "username": username,
                "password": "testpassword123"
            }
        )

    def data(self, **changes):
        result = {
            "employee_code": "EMP-001",
            "first_name": "Aarav",
            "last_name": "Sharma",
            "email": "aarav@example.com",
            "phone": "9876543210",
            "department": "Kitchen",
            "job_title": "Chef",
            "hire_date": "2026-01-15",
            "employment_status": "active"
        }

        result.update(changes)

        return result

    def create(self, **changes):
        return self.client.post(
            "/api/employees",
            json=self.data(**changes)
        )

    def test_owner_can_create_and_view_employee(self):
        self.login("employeeowner")

        created = self.create()

        self.assertEqual(created.status_code, 201)

        self.assertEqual(
            created.get_json()["employee"]["name"],
            "Aarav Sharma"
        )

        listing = self.client.get("/api/employees")

        self.assertEqual(listing.status_code, 200)

        self.assertEqual(
            len(listing.get_json()["employees"]),
            1
        )

    def test_duplicate_employee_code_is_rejected(self):
        self.login("employeeowner")

        self.create()

        response = self.create(
            email="other@example.com"
        )

        self.assertEqual(response.status_code, 409)

    def test_duplicate_email_is_rejected(self):
        self.login("employeeowner")

        self.create()

        response = self.create(
            employee_code="EMP-002",
            email="aarav@example.com"
        )

        self.assertEqual(response.status_code, 409)

    def test_required_fields_are_validated(self):
        self.login("employeeowner")

        response = self.client.post(
            "/api/employees",
            json={
                "employee_code": "EMP-003"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_owner_can_edit_employee(self):
        self.login("employeeowner")

        employee_id = self.create().get_json()["employee"]["id"]

        response = self.client.put(
            f"/api/employees/{employee_id}",
            json=self.data(job_title="Senior Chef")
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["employee"]["job_title"],
            "Senior Chef"
        )

    def test_owner_can_deactivate_employee(self):
        self.login("employeeowner")

        employee_id = self.create().get_json()["employee"]["id"]

        response = self.client.patch(
            f"/api/employees/{employee_id}/status",
            json={
                "employment_status": "inactive"
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["employee"]["employment_status"],
            "inactive"
        )

    def test_invalid_status_is_rejected(self):
        self.login("employeeowner")

        employee_id = self.create().get_json()["employee"]["id"]

        response = self.client.patch(
            f"/api/employees/{employee_id}/status",
            json={
                "employment_status": "terminated"
            }
        )

        self.assertEqual(response.status_code, 400)

    def test_assistant_manager_can_view_but_cannot_create(self):
        self.login("employeeowner")

        self.create()

        self.client.post("/auth/logout")

        self.login("employeeassistant")

        self.assertEqual(
            self.client.get("/api/employees").status_code,
            200
        )

        response = self.create(
            employee_code="EMP-002",
            email="second@example.com"
        )

        self.assertEqual(response.status_code, 403)

    def test_search_and_status_filter(self):
        self.login("employeeowner")

        self.create()

        self.create(
            employee_code="EMP-002",
            first_name="Riya",
            email="riya@example.com",
            employment_status="inactive"
        )

        search = self.client.get(
            "/api/employees?search=Riya"
        )

        inactive = self.client.get(
            "/api/employees?status=inactive"
        )

        self.assertEqual(
            len(search.get_json()["employees"]),
            1
        )

        self.assertEqual(
            len(inactive.get_json()["employees"]),
            1
        )

    def test_employee_page_loads(self):
        self.login("employeeowner")

        response = self.client.get("/employees")

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()