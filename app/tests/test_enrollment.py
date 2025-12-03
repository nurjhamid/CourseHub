import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.tests.conftest import create_in_memory_db
from app.models import database as db_mod

class EnrollmentTests(unittest.TestCase):
    def setUp(self):
        engine, SessionLocal = create_in_memory_db()
        def override_get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        app.dependency_overrides[db_mod.get_db] = override_get_db
        self.client = TestClient(app)
        # create admin and course and student
        self.client.post("/auth/register", json={"username":"admin1","email":"a@a.com","password":"pw","phone":"p","address":"a","role":"admin","name":"Admin"})
        r = self.client.post("/auth/login", json={"username":"admin1","password":"pw"})
        admin = r.json()
        self.client.post("/courses/", json={"admin_id": admin["user_id"], "course_name":"BIO101", "credits":3, "max_students":2})
        self.client.post("/auth/register", json={"username":"s1","email":"s1@ex.com","password":"pw","phone":"p","address":"a","role":"student","name":"S1"})
        r2 = self.client.post("/auth/login", json={"username":"s1","password":"pw"})
        self.student = r2.json()

    def tearDown(self):
        app.dependency_overrides = {}

    def test_student_enroll(self):
        # list courses to get id
        courses = self.client.get("/courses/").json()
        cid = courses[0]["course_id"]
        res = self.client.post("/courses/enroll", json={"user_id": self.student["user_id"], "course_id": cid})
        self.assertEqual(res.status_code, 200)
        self.assertIn("enrollment_id", res.json())

    def test_student_double_enroll_fails(self):
        courses = self.client.get("/courses/").json()
        cid = courses[0]["course_id"]
        self.client.post("/courses/enroll", json={"user_id": self.student["user_id"], "course_id": cid})
        r2 = self.client.post("/courses/enroll", json={"user_id": self.student["user_id"], "course_id": cid})
        self.assertEqual(r2.status_code, 400)

    def test_unenroll(self):
        courses = self.client.get("/courses/").json()
        cid = courses[0]["course_id"]
        enr = self.client.post("/courses/enroll", json={"user_id": self.student["user_id"], "course_id": cid}).json()
        eid = enr["enrollment_id"]
        r = self.client.delete(f"/courses/enroll/{eid}?user_id={self.student['user_id']}")
        self.assertEqual(r.status_code, 200)
        self.assertIn("cancelled", r.json()["message"].lower())

if __name__ == "__main__":
    unittest.main()
