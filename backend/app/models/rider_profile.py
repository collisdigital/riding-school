import uuid6
from sqlalchemy import Column, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin


class RiderProfile(Base, TimestampMixin, TenantMixin, SoftDeleteMixin):
    __tablename__ = "rider_profiles"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False, index=True)
    school_id = Column(Uuid, ForeignKey("schools.id"), nullable=False, index=True)

    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    date_of_birth = Column(Date, nullable=True)

    user = relationship("User", back_populates="rider_profiles")
    school = relationship("School", back_populates="rider_profiles")
    grade_history = relationship(
        "RiderGradeHistory", back_populates="rider", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<RiderProfile(id='{self.id}')>"
