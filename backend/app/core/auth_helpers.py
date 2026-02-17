import uuid
from datetime import UTC, datetime

from fastapi import Response
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.membership import Membership, MembershipRole
from app.models.role import Role


def get_user_permissions(
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


def set_access_cookie(response: Response, access_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
    )


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    rt_expire: datetime,
) -> None:
    set_access_cookie(response, access_token)

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
