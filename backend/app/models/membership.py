import uuid6
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, TimestampMixin, TenantMixin


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    school_id = Column(Uuid, ForeignKey("schools.id"), nullable=False, index=True)

    user = relationship("User", back_populates="memberships")
    school = relationship("School", back_populates="memberships")
    roles = relationship("MembershipRole", back_populates="membership", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("user_id", "school_id", name="uq_user_school"),)


class MembershipRole(Base):
    __tablename__ = "membership_roles"

    membership_id = Column(Uuid, ForeignKey("memberships.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    membership = relationship("Membership", back_populates="roles")
    role = relationship("Role", back_populates="membership_roles")
