import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db import get_db
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.user import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_token_payload(
    request: Request, token: str | None = Depends(reusable_oauth2)
) -> TokenPayload:
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    return token_data


def get_current_user(
    db: Session = Depends(get_db), token_data: TokenPayload = Depends(get_token_payload)
) -> User:
    try:
        user_id = uuid.UUID(token_data.sub)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token subject") from None

    # Load user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine school context
    school_id = None
    if token_data.school_id:
        try:
            school_id = uuid.UUID(token_data.school_id)
        except ValueError:
            pass

    # Find membership
    if school_id:
        membership = (
            db.query(Membership)
            .options(
                joinedload(Membership.roles)
                .joinedload(MembershipRole.role)
                .joinedload(Role.permissions),
                joinedload(Membership.school),
            )
            .filter(
                Membership.user_id == user.id,
                Membership.school_id == school_id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(status_code=403, detail="Not a member of this school")
    else:
        # No school in token (e.g. first login, or global admin?)
        # Default to first membership
        membership = (
            db.query(Membership)
            .options(
                joinedload(Membership.roles)
                .joinedload(MembershipRole.role)
                .joinedload(Role.permissions),
                joinedload(Membership.school),
            )
            .filter(Membership.user_id == user.id)
            .first()
        )

    if membership:
        # Attach context to user instance (transient)
        user.school_id = membership.school_id
        user.school = membership.school
        user.current_membership = membership
        # Flatten roles
        user.roles = [mr.role for mr in membership.roles]
    else:
        user.school_id = None
        user.school = None
        user.roles = []

    return user


def get_current_active_school_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not getattr(current_user, "school_id", None):
        raise HTTPException(
            status_code=400,
            detail="User is not associated with any school context",
        )
    return current_user


class RequirePermission:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, current_user: User = Depends(get_current_active_school_user)):
        # Check if user has permission
        if not current_user.current_membership:
             # Should be caught by get_current_active_school_user but safe check
             raise HTTPException(status_code=403, detail="No active membership")

        # Use the property added to Membership
        user_perms = current_user.current_membership.permissions
        if self.required_permission not in user_perms:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.required_permission}",
            )
        return current_user
