import uuid6
from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, TenantMixin, TimestampMixin


class RiderGradeHistory(Base, TenantMixin, TimestampMixin):
    __tablename__ = "rider_grade_history"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    rider_id = Column(Uuid, ForeignKey("rider_profiles.id"), nullable=False, index=True)
    grade_id = Column(Uuid, ForeignKey("grades.id"), nullable=False, index=True)
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    rider = relationship("RiderProfile", back_populates="grade_history")
    grade = relationship("Grade", back_populates="rider_history")
    school = relationship("School", back_populates="rider_grade_history")

    def __repr__(self):
        return (
            f"<RiderGradeHistory(id='{self.id}', "
            f"rider_id='{self.rider_id}', grade_id='{self.grade_id}')>"
        )
