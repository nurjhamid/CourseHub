import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.tests.conftest import create_in_memory_db
from app.models.database import Base
from app.models import database as db_mod

class AuthTests(unittest.TestCase):
    def setUp(self):
        engine, SessionLocal = create_in_memory_db()
        # patch the app dependency
        def override_get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        app.dependency_overrides[db_mod.get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides = {}

    def test_register_student(self):
        payload = {
            "username": "s1",
            "email": "s1@example.com",
            "password": "pw",
            "phone": "123",
            "address": "addr",
            "role": "student",
            "name": "Student One"
        }
        res = self.client.post("/auth/register", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("user_id", data)
        self.assertEqual(data["role"], "student")

    def test_register_duplicate(self):
        payload = {
            "username": "s2",
            "email": "s2@example.com",
            "password": "pw",
            "phone": "123",
            "address": "addr",
            "role": "student",
            "name": "Student Two"
        }
        r1 = self.client.post("/auth/register", json=payload)
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post("/auth/register", json=payload)
        self.assertEqual(r2.status_code, 400)

    def test_login_success_and_fail(self):
        reg = {
            "username": "u1",
            "email": "u1@ex.com",
            "password": "secret",
            "phone": "p",
            "address": "a",
            "role": "student",
            "name": "U One"
        }
        self.client.post("/auth/register", json=reg)
        r = self.client.post("/auth/login", json={"username":"u1","password":"secret"})
        self.assertEqual(r.status_code, 200)
        bad = self.client.post("/auth/login", json={"username":"u1","password":"wrong"})
        self.assertEqual(bad.status_code, 401)

if __name__ == "__main__":
    unittest.main()
