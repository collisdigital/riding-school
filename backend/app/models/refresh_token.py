import uuid6
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.types import Uuid

from .base import Base, TimestampMixin


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    # ID of the new token replacing this one
    replaced_by = Column(String, nullable=True)
