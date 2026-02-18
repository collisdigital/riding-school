from typing import ClassVar

from sqlalchemy import Column, ForeignKey, Integer, String, Table, event
from sqlalchemy.orm import Session, relationship

from .base import Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Static roles
    ADMIN = "ADMIN"
    INSTRUCTOR = "INSTRUCTOR"
    PARENT = "PARENT"
    RIDER = "RIDER"

    # Cache for role IDs to avoid redundant lookups
    _id_cache: ClassVar[dict[str, int]] = {}
    _pending_cache_key: ClassVar[str] = "_pending_role_id_cache"

    @classmethod
    def get_id(cls, db: Session, name: str) -> int | None:
        """
        Get role ID by name, using in-memory cache if available.
        """
        if name in cls._id_cache:
            return cls._id_cache[name]

        role = db.query(cls).filter(cls.name == name).first()
        if role:
            cls.stage_cache_update(db, name, role.id)
            return role.id
        return None

    @classmethod
    def get_cached_id(cls, name: str) -> int | None:
        return cls._id_cache.get(name)

    @classmethod
    def stage_cache_update(cls, db: Session, name: str, role_id: int) -> None:
        pending = db.info.setdefault(cls._pending_cache_key, {})
        pending[name] = role_id

    @classmethod
    def clear_cache(cls):
        """Clear the role ID cache."""
        cls._id_cache.clear()

    membership_roles = relationship("MembershipRole", back_populates="role")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


@event.listens_for(Session, "after_commit")
def _flush_pending_role_cache(session: Session) -> None:
    pending = session.info.pop(Role._pending_cache_key, {})
    Role._id_cache.update(pending)


@event.listens_for(Session, "after_rollback")
def _clear_pending_role_cache(session: Session) -> None:
    session.info.pop(Role._pending_cache_key, None)
