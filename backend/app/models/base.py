import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TenantMixin:
    @declared_attr
    def school_id(cls):
        return Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
