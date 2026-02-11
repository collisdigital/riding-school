import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, TimestampMixin

# Association table for Role <-> Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Uuid,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Uuid,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# Association table for User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Uuid,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(
        String, unique=True, index=True, nullable=False
    )  # e.g., 'riders:view'
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<Permission(name='{self.name}')>"


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)  # e.g., 'Instructor'
    description = Column(String, nullable=True)

    permissions = relationship(
        "Permission", secondary=role_permissions, backref="roles"
    )

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class UserPermissionOverride(Base, TimestampMixin):
    __tablename__ = "user_permission_overrides"

    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(
        Uuid,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    allow = Column(Boolean, default=True)  # True = allow, False = explicitly deny

    permission = relationship("Permission")


class Relationship(Base, TimestampMixin):
    __tablename__ = "relationships"

    parent_id = Column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    rider_id = Column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    relation_type = Column(String, default="PARENT")  # e.g., 'PARENT', 'GUARDIAN'

    parent = relationship(
        "User", foreign_keys=[parent_id], back_populates="child_relationships"
    )
    rider = relationship(
        "User", foreign_keys=[rider_id], back_populates="parent_relationships"
    )
