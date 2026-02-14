import uuid6
from sqlalchemy import Column, DateTime, ForeignKey, event
from sqlalchemy.orm import DeclarativeBase, declared_attr, Session, with_loader_criteria
from sqlalchemy.sql import func
from sqlalchemy.types import Uuid


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class TenantMixin:
    @declared_attr
    def school_id(cls):
        return Column(
            Uuid(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True
        )


@event.listens_for(Session, "do_orm_execute")
def _add_filtering_criteria(execute_state):
    """
    Automatically add a filter for soft-deleted records.
    If the query involves a model with SoftDeleteMixin,
    filter out records where deleted_at is not None.
    To include deleted records, add execution_options(include_deleted=True).
    """
    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at.is_(None),
                include_aliases=True,
            )
        )
