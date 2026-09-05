from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.auth_service import AuthService, get_current_user
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication & User Access"])

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "FARMER"
    phone: Optional[str] = None
    location: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class DemoLoginRequest(BaseModel):
    role: str # 'farmer', 'expert', 'admin'

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register New User")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    return AuthService.register_user(
        db=db,
        name=req.name,
        email=req.email,
        password=req.password,
        role=req.role or "FARMER",
        phone=req.phone,
        location=req.location
    )

@router.post("/login", summary="User Login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.authenticate_user(db=db, email=req.email, password=req.password)

@router.post("/demo-login", summary="1-Click Demo Evaluation Login")
def demo_login(req: DemoLoginRequest, db: Session = Depends(get_db)):
    return AuthService.get_demo_user(db=db, role=req.role)

@router.get("/me", summary="Get Current Authenticated User")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "verification_status": user.verification_status,
        "account_status": user.account_status,
        "farmer_code": user.farmer_code,
        "location": user.location,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }
