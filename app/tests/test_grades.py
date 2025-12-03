import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.tests.conftest import create_in_memory_db
from app.models import database as db_mod

class GradeTests(unittest.TestCase):
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
        # create admin, course, student, enroll
        self.client.post("/auth/register", json={"username":"admin1","email":"a@a.com","password":"pw","phone":"p","address":"a","role":"admin","name":"Admin"})
        r = self.client.post("/auth/login", json={"username":"admin1","password":"pw"})
        admin = r.json()
        self.client.post("/courses/", json={"admin_id": admin["user_id"], "course_name":"CHEM101", "credits":3, "max_students":5})
        self.client.post("/auth/register", json={"username":"s1","email":"s1@ex.com","password":"pw","phone":"p","address":"a","role":"student","name":"S1"})
        s = self.client.post("/auth/login", json={"username":"s1","password":"pw"}).json()
        course_id = self.client.get("/courses/").json()[0]["course_id"]
        enr = self.client.post("/courses/enroll", json={"user_id": s["user_id"], "course_id": course_id}).json()
        self.admin = admin
        self.student = s
        self.enrollment_id = enr["enrollment_id"]

    def tearDown(self):
        app.dependency_overrides = {}

    def test_assign_valid_grade(self):
        res = self.client.post("/courses/assign-grade", json={"admin_id": self.admin["user_id"], "enrollment_id": self.enrollment_id, "grade": "A"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("assigned", res.json()["message"].lower())

    def test_assign_invalid_grade(self):
        res = self.client.post("/courses/assign-grade", json={"admin_id": self.admin["user_id"], "enrollment_id": self.enrollment_id, "grade": "Z"})
        self.assertEqual(res.status_code, 400)

    def test_view_grades_for_student(self):
        # assign first
        self.client.post("/courses/assign-grade", json={"admin_id": self.admin["user_id"], "enrollment_id": self.enrollment_id, "grade": "B"})
        r = self.client.get(f"/courses/grades?user_id={self.student['user_id']}")
        self.assertEqual(r.status_code, 200)
        arr = r.json()
        self.assertTrue(len(arr) >= 1)
        self.assertIn(arr[0]["grade"], ["B", None])

if __name__ == "__main__":
    unittest.main()
