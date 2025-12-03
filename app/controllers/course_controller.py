from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.course_model import (
    User,
    Student,
    Admin,
    Course,
    Enrollment,
    get_student_by_user_id,
    is_admin,
    enroll_student_in_course,
    validate_grade,
)

router = APIRouter()

class CourseCreate(BaseModel):
    admin_id: int
    course_name: str
    description: str | None = None
    credits: int
    max_students: int = 50

class CourseUpdate(BaseModel):
    admin_id: int
    course_name: str | None = None
    description: str | None = None
    credits: int | None = None
    max_students: int | None = None

class EnrollmentRequest(BaseModel):
    user_id: int
    course_id: int

class AssignGradePayload(BaseModel):
    admin_id: int
    enrollment_id: int
    grade: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if not is_admin(db, payload.admin_id):
        raise HTTPException(status_code=403, detail="Only admins can create courses.")

    existing = db.query(Course).filter(Course.course_name == payload.course_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course name already exists.")

    course = Course(
        course_name=payload.course_name,
        description=payload.description,
        credits=payload.credits,
        max_students=payload.max_students,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return {
        "course_id": course.course_id,
        "course_name": course.course_name,
        "description": course.description,
        "credits": course.credits,
        "max_students": course.max_students,
    }

@router.put("/{course_id}")
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    if not is_admin(db, payload.admin_id):
        raise HTTPException(status_code=403, detail="Only admins can update courses.")

    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    if payload.course_name is not None:
        course.course_name = payload.course_name
    if payload.description is not None:
        course.description = payload.description
    if payload.credits is not None:
        course.credits = payload.credits
    if payload.max_students is not None:
        course.max_students = payload.max_students

    db.commit()
    db.refresh(course)

    return {
        "course_id": course.course_id,
        "course_name": course.course_name,
        "description": course.description,
        "credits": course.credits,
        "max_students": course.max_students,
    }

@router.delete("/{course_id}")
def delete_course(course_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)) -> Dict[str, str]:
    if not is_admin(db, admin_id):
        raise HTTPException(status_code=403, detail="Only admins can delete courses.")

    course = db.query(Course).filter(Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully."}

@router.get("/")
def list_courses(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    courses = db.query(Course).all()
    return [
        {
            "course_id": c.course_id,
            "course_name": c.course_name,
            "description": c.description,
            "credits": c.credits,
            "max_students": c.max_students,
        }
        for c in courses
    ]

@router.get("/{course_id}/students")
def get_students_for_course(course_id: int, admin_id: int = Query(...), db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    if not is_admin(db, admin_id):
        raise HTTPException(status_code=403, detail="Only admins can view enrolled students.")

    enrollments = db.query(Enrollment).join(Student).filter(Enrollment.course_id == course_id).all()

    return [
        {
            "enrollment_id": e.enrollment_id,
            "student_id": e.student.student_id,
            "student_name": e.student.name,
            "user_id": e.student.user_id,
            "grade": e.grade,
            "date_enrolled": e.date_enrolled,
        }
        for e in enrollments
    ]

@router.post("/enroll")
def enroll_in_course(payload: EnrollmentRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    student = get_student_by_user_id(db, payload.user_id)
    if not student:
        raise HTTPException(status_code=403, detail="Only students can enroll.")

    course = db.query(Course).filter(Course.course_id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    try:
        enrollment = enroll_student_in_course(db, student, course)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {
        "enrollment_id": enrollment.enrollment_id,
        "student_id": enrollment.student_id,
        "course_id": enrollment.course_id,
        "date_enrolled": enrollment.date_enrolled,
        "grade": enrollment.grade,
    }

@router.delete("/enroll/{enrollment_id}")
def leave_course(enrollment_id: int, user_id: int = Query(...), db: Session = Depends(get_db)) -> Dict[str, str]:
    student = get_student_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=403, detail="Only students can leave courses.")

    enrollment = db.query(Enrollment).filter(
        Enrollment.enrollment_id == enrollment_id,
        Enrollment.student_id == student.student_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found.")

    db.delete(enrollment)
    db.commit()
    return {"message": "Enrollment cancelled successfully."}

@router.get("/my-enrollments")
def get_enrollments_for_student(user_id: int = Query(...), db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    student = get_student_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=403, detail="Only students can view enrollments.")

    enrollments = db.query(Enrollment).join(Course).filter(Enrollment.student_id == student.student_id).all()

    return [
        {
            "enrollment_id": e.enrollment_id,
            "course_id": e.course.course_id,
            "course_name": e.course.course_name,
            "description": e.course.description,
            "credits": e.course.credits,
            "date_enrolled": e.date_enrolled,
            "grade": e.grade,
        }
        for e in enrollments
    ]

@router.post("/assign-grade")
def assign_grade(payload: AssignGradePayload, db: Session = Depends(get_db)) -> Dict[str, str]:
    if not is_admin(db, payload.admin_id):
        raise HTTPException(status_code=403, detail="Only admins can assign grades.")

    if not validate_grade(payload.grade):
        raise HTTPException(status_code=400, detail="Invalid grade.")

    enrollment = db.query(Enrollment).filter(Enrollment.enrollment_id == payload.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found.")

    enrollment.grade = payload.grade
    db.commit()
    return {"message": "Grade assigned successfully."}

@router.get("/grades")
def view_grades_for_student(user_id: int = Query(...), db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    student = get_student_by_user_id(db, user_id)
    if not student:
        raise HTTPException(status_code=403, detail="Only students can view grades.")

    enrollments = db.query(Enrollment).join(Course).filter(Enrollment.student_id == student.student_id).all()

    return [
        {
            "course_name": e.course.course_name,
            "credits": e.course.credits,
            "grade": e.grade,
        }
        for e in enrollments
    ]
