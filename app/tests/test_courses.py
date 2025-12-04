import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.tests.conftest import create_in_memory_db
from app.models import database as db_mod

class CourseTests(unittest.TestCase):
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
        
        self.client.post("/auth/register", json={
            "username":"admin1","email":"a@a.com","password":"pw","phone":"p","address":"a","role":"admin","name":"Admin"
        })

    def tearDown(self):
        app.dependency_overrides = {}

    def test_create_course_by_admin(self):
        
        r = self.client.post("/auth/login", json={"username":"admin1","password":"pw"})
        admin = r.json()
        payload = {"admin_id": admin["user_id"], "course_name":"Math 101", "credits":3, "max_students":10}
        res = self.client.post("/courses/", json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()["course_name"], "Math 101")

    def test_create_duplicate_course(self):
        r = self.client.post("/auth/login", json={"username":"admin1","password":"pw"})
        admin = r.json()
        payload = {"admin_id": admin["user_id"], "course_name":"CS101", "credits":4, "max_students":5}
        r1 = self.client.post("/courses/", json=payload)
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post("/courses/", json=payload)
        self.assertEqual(r2.status_code, 400)

    def test_delete_course(self):
        r = self.client.post("/auth/login", json={"username":"admin1","password":"pw"})
        admin = r.json()
        payload = {"admin_id": admin["user_id"], "course_name":"HIST", "credits":2, "max_students":5}
        r1 = self.client.post("/courses/", json=payload)
        cid = r1.json()["course_id"]
        res = self.client.delete(f"/courses/{cid}?admin_id={admin['user_id']}")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Course deleted", res.json()["message"])

if __name__ == "__main__":
    unittest.main()

