import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.ratelimit import RateLimiter
from app.db import get_db
from app.models.membership import Membership
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserSchema, UserWithSchool

router = APIRouter()
login_limiter = RateLimiter(requests_limit=5, time_window=60)


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
        is_active=True,
    )
    db.add(db_obj)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to register user") from None
    db.refresh(db_obj)
    return db_obj


@router.post("/login", response_model=Token, dependencies=[Depends(login_limiter)])
def login(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = db.query(User).filter(User.email == form_data.username).first()

    # Check if user exists and has a password set (managed users might not)
    if (
        not user
        or not user.hashed_password
        or not security.verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Find school context
    # If client sends X-School-ID header, we could use that.
    # For now, default to the first membership found.
    membership = db.query(Membership).filter(Membership.user_id == user.id).first()
    school_id = membership.school_id if membership else None

    access_token = security.create_access_token(user.id, school_id=school_id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}
