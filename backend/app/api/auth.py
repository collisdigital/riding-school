import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.ratelimit import RateLimiter
from app.db import get_db
from app.models.membership import Membership, MembershipRole
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserSchema, UserWithSchool

router = APIRouter()
login_limiter = RateLimiter(
    requests_limit=5,
    time_window=60,
    error_message="Too many login attempts. Please try again later.",
)
register_limiter = RateLimiter(
    requests_limit=5,
    time_window=60,
    error_message="Too many registration attempts. Please try again later.",
)


@router.get("/me", response_model=UserWithSchool)
def get_me(current_user: User = Depends(deps.get_current_user)):
    return current_user


@router.post(
    "/register", response_model=UserSchema, dependencies=[Depends(register_limiter)]
)
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


def _get_user_permissions(
    db: Session, user_id: uuid.UUID
) -> tuple[uuid.UUID | None, list[str], list[str]]:
    """
    Fetch school_id, permissions, and roles for a user eagerly.
    """
    membership = (
        db.query(Membership)
        .options(
            joinedload(Membership.roles)
            .joinedload(MembershipRole.role)
            .joinedload(Role.permissions),
            joinedload(Membership.school),
        )
        .filter(Membership.user_id == user_id)
        .first()
    )

    school_id = None
    perms = []
    roles = []

    if membership:
        school_id = membership.school_id
        perms = membership.permissions
        roles = [mr.role.name for mr in membership.roles if mr.role]

    return school_id, perms, roles


def _set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    rt_expire: datetime,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
    )

    rt_max_age = int((rt_expire - datetime.now(UTC)).total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=rt_max_age,
        expires=int(rt_expire.timestamp()),
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        path="/api/auth",
    )


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

    school_id, perms, roles = _get_user_permissions(db, user.id)

    access_token = security.create_access_token(
        user.id, school_id=school_id, perms=perms, roles=roles
    )

    # Create and store refresh token
    rt_token, rt_hash, rt_expire = security.create_refresh_token(user.id)
    rt_db = RefreshToken(user_id=user.id, token_hash=rt_hash, expires_at=rt_expire)
    db.add(rt_db)
    db.commit()

    _set_auth_cookies(response, access_token, rt_token, rt_expire)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    rt_hash = security.get_token_hash(refresh_token)

    # Find token in DB
    rt_db = (
        db.query(RefreshToken).filter(RefreshToken.token_hash == rt_hash).first()
    )

    if not rt_db:
        response.delete_cookie("refresh_token", path="/api/auth")
        response.delete_cookie("access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    if rt_db.revoked_at or rt_db.replaced_by:
        # Revoked or used
        response.delete_cookie("refresh_token", path="/api/auth")
        response.delete_cookie("access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
        )

    # Ensure timezone awareness for comparison (SQLite compat)
    expires_at = rt_db.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if expires_at < datetime.now(UTC):
        # Expired
        response.delete_cookie("refresh_token", path="/api/auth")
        response.delete_cookie("access_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )

    user = db.get(User, rt_db.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive"
        )

    school_id, perms, roles = _get_user_permissions(db, user.id)

    new_access_token = security.create_access_token(
        user.id, school_id=school_id, perms=perms, roles=roles
    )

    # Rotate Refresh Token
    new_rt, new_rt_hash, new_rt_expire = security.create_refresh_token(user.id)

    # Mark old as revoked/replaced
    rt_db.revoked_at = datetime.now(UTC)

    new_rt_db = RefreshToken(
        user_id=user.id, token_hash=new_rt_hash, expires_at=new_rt_expire
    )
    db.add(new_rt_db)
    db.flush()  # Get ID

    rt_db.replaced_by = str(new_rt_db.id)
    db.commit()

    _set_auth_cookies(response, new_access_token, new_rt, new_rt_expire)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        rt_hash = security.get_token_hash(refresh_token)
        rt_db = (
            db.query(RefreshToken).filter(RefreshToken.token_hash == rt_hash).first()
        )
        if rt_db:
            rt_db.revoked_at = datetime.now(UTC)
            db.commit()

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/auth")
    return {"message": "Successfully logged out"}
