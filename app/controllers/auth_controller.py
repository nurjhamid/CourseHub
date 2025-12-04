from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.course_model import User, Student, Admin

router = APIRouter()

class RegisterPayload(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: str
    address: str
    role: str = "student"  
    name: str

class LoginPayload(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    existing = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    user = User(
        username=payload.username,
        password=payload.password,  # plain text for academic prototype only
        email=payload.email,
        phone=payload.phone,
        address=payload.address,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.role == "student":
        student = Student(name=payload.name, user_id=user.user_id)
        db.add(student)
    else:
        admin = Admin(user_id=user.user_id)
        db.add(admin)

    db.commit()

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "role": user.role,
    }

@router.post("/login")
def login_user(payload: LoginPayload, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }
