import unittest
from app.tests.conftest import create_in_memory_db
from app.models.course_model import validate_grade, enroll_student_in_course
from app.models import database as db_mod

class ModelTests(unittest.TestCase):
    def setUp(self):
        engine, SessionLocal = create_in_memory_db()
        self.SessionLocal = SessionLocal
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_validate_grade(self):
        self.assertTrue(validate_grade("A"))
        self.assertFalse(validate_grade("Z"))

    def test_enroll_logic_raises_if_full(self):
    
        from app.models.course_model import Course, Student, Enrollment, User, Base
        c = Course(course_name="LimitCourse", credits=1, max_students=1)
        u1 = User(username="u1", password="p", email="u1@ex.com", phone="p", address="a", role="student")
        u2 = User(username="u2", password="p", email="u2@ex.com", phone="p", address="a", role="student")
        s1 = Student(name="S1")
        s2 = Student(name="S2")
        
        self.db.add(u1); self.db.flush()
        s1.user_id = u1.user_id
        self.db.add(s1)
        self.db.add(c)
        self.db.commit()
        
        enroll_student_in_course(self.db, s1, c)
        
        self.db.add(u2); self.db.flush()
        s2.user_id = u2.user_id
        self.db.add(s2); self.db.commit()
        with self.assertRaises(ValueError):
            enroll_student_in_course(self.db, s2, c)

    def test_enroll_duplicates(self):
        from app.models.course_model import Course, Student, User
        c = Course(course_name="DupCourse", credits=1, max_students=5)
        u = User(username="ud", password="p", email="ud@ex.com", phone="p", address="a", role="student")
        s = Student(name="S")
        self.db.add(u); self.db.flush()
        s.user_id = u.user_id
        self.db.add(s)
        self.db.add(c); self.db.commit()
        enroll_student_in_course(self.db, s, c)
        with self.assertRaises(ValueError):
            enroll_student_in_course(self.db, s, c)

if __name__ == "__main__":
    unittest.main()

