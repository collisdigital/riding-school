from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.sql import func
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TenantMixin:
    @declared_attr
    def school_id(cls):
        return Column(
            Uuid(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True
        )
