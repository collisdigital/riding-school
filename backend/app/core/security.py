import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: str | Any,
    school_id: str = None,
    roles: list[str] = None,
    perms: list[str] = None,
    expires_delta: timedelta = None,
) -> str:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    if school_id:
        to_encode["sid"] = str(school_id)
    if roles:
        to_encode["roles"] = roles
    if perms:
        to_encode["perms"] = perms

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str | Any, expires_delta: timedelta = None
) -> tuple[str, str, datetime]:
    """
    Generates a random refresh token, its hash, and expiration time.
    Returns (token, token_hash, expires_at)
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    token = secrets.token_urlsafe(32)
    token_hash = get_token_hash(token)
    return token, token_hash, expire


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_token_hash(token: str) -> str:
    """
    Returns SHA256 hash of the token string.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    return secrets.compare_digest(get_token_hash(token), token_hash)
