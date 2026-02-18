from typing import ClassVar

from sqlalchemy import Column, ForeignKey, Integer, String, Table
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

    @classmethod
    def get_id(cls, db: Session, name: str) -> int | None:
        """
        Get role ID by name, using in-memory cache if available.
        """
        if name in cls._id_cache:
            return cls._id_cache[name]

        role = db.query(cls).filter(cls.name == name).first()
        if role:
            cls._id_cache[name] = role.id
            return role.id
        return None

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
