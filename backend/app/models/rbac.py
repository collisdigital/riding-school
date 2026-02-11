import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

# Association table for Role <-> Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for User <-> Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False) # e.g., 'riders:view'
    description = Column(String, nullable=True)

    def __repr__(self):
        return f"<Permission(name='{self.name}')>"

class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False) # e.g., 'Instructor'
    description = Column(String, nullable=True)

    permissions = relationship("Permission", secondary=role_permissions, backref="roles")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"

class UserPermissionOverride(Base, TimestampMixin):
    __tablename__ = "user_permission_overrides"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    allow = Column(Boolean, default=True) # True = allow, False = explicitly deny

class Relationship(Base, TimestampMixin):
    __tablename__ = "relationships"

    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    rider_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    relation_type = Column(String, default="PARENT") # e.g., 'PARENT', 'GUARDIAN'

    parent = relationship("User", foreign_keys=[parent_id], back_populates="child_relationships")
    rider = relationship("User", foreign_keys=[rider_id], back_populates="parent_relationships")
