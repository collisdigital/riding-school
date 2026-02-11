import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db import get_db
from app.models.rbac import Role, UserPermissionOverride
from app.models.user import User
from app.schemas import TokenPayload

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

    user = (
        db.query(User)
        .options(
            joinedload(User.school),
            joinedload(User.roles).joinedload(Role.permissions),
            joinedload(User.permission_overrides).joinedload(
                UserPermissionOverride.permission
            ),
        )
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user_simple(
    db: Session = Depends(get_db), token_data: TokenPayload = Depends(get_token_payload)
) -> User:
    try:
        user_id = uuid.UUID(token_data.sub)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token subject") from None

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_permissions(user: User) -> set:
    permissions = set()
    # Add from roles
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)

    # Add/Remove from overrides
    for override in user.permission_overrides:
        if override.allow:
            permissions.add(override.permission.name)
        else:
            permissions.discard(override.permission.name)

    return permissions


def check_permissions(required_permissions: list[str]):
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_perms = get_user_permissions(current_user)
        for perm in required_permissions:
            if perm not in user_perms:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm}",
                )
        return current_user

    return permission_checker


def get_current_active_school_user(
    current_user: User = Depends(get_current_user_simple),
) -> User:
    if not current_user.school_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with any school"
        )
    return current_user
