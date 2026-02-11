from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db
from app.core import security
from app.models.user import User, UserRole
from app.schemas import UserCreate, UserSchema, Token, UserWithSchool
from app.api import deps
from datetime import timedelta

router = APIRouter()

@router.get("/me", response_model=UserWithSchool)
def get_me(current_user: User = Depends(deps.get_current_user)):
    return current_user

@router.post("/register", response_model=UserSchema)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    db_obj = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        role=UserRole.RIDER, # Default role
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    return {
        "access_token": security.create_access_token(
            user.id, school_id=user.school_id
        ),
        "token_type": "bearer",
    }
