import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
from .rbac import user_roles

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id", ondelete="SET NULL"), nullable=True)
    school = relationship("School", back_populates="users")

    # RBAC
    roles = relationship("Role", secondary=user_roles, backref="users")
    permission_overrides = relationship("UserPermissionOverride", backref="user", cascade="all, delete-orphan")

    # Parent-Child Relationships
    child_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    parent_relationships = relationship(
        "Relationship",
        foreign_keys="Relationship.rider_id",
        back_populates="rider",
        cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User(email='{self.email}')>"
