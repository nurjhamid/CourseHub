from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Session

from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'student' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)

class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)

    user = relationship("User", back_populates="student")
    enrollments = relationship("Enrollment", back_populates="student")

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), default="course_admin")
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)

    user = relationship("User", back_populates="admin")

class Course(Base):
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    credits = Column(Integer, nullable=False)
    max_students = Column(Integer, nullable=False, default=50)

    enrollments = relationship("Enrollment", back_populates="course")

class Enrollment(Base):
    __tablename__ = "enrollments"

    enrollment_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    date_enrolled = Column(DateTime, default=datetime.utcnow)
    grade = Column(String(5), nullable=True)

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

# Business helpers
def get_student_by_user_id(db: Session, user_id: int) -> Optional[Student]:
    return (
        db.query(Student)
        .join(User)
        .filter(User.user_id == user_id, User.role == "student")
        .first()
    )

def is_admin(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.user_id == user_id).first()
    return bool(user and user.role == "admin")

def enroll_student_in_course(db: Session, student: Student, course: Course) -> Enrollment:
    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == student.student_id,
            Enrollment.course_id == course.course_id,
        )
        .first()
    )
    if existing:
        raise ValueError("Student is already enrolled in this course.")

    count = db.query(Enrollment).filter(Enrollment.course_id == course.course_id).count()
    if count >= course.max_students:
        raise ValueError("Course is full.")

    enrollment = Enrollment(student_id=student.student_id, course_id=course.course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment

def validate_grade(grade: str) -> bool:
    allowed = {"A", "B", "C", "D", "F", "I"}
    return grade in allowed
