import uuid6
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, SoftDeleteMixin, TenantMixin, TimestampMixin


class Grade(Base, TenantMixin, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "grades"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False, default=0)

    # Relationships
    skills = relationship("Skill", back_populates="grade", cascade="all, delete-orphan")
    school = relationship("School", back_populates="grades")
    rider_history = relationship("RiderGradeHistory", back_populates="grade")

    def __repr__(self):
        return f"<Grade(id='{self.id}', name='{self.name}')>"


class Skill(Base, TenantMixin, SoftDeleteMixin, TimestampMixin):
    __tablename__ = "skills"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    grade_id = Column(Uuid, ForeignKey("grades.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Relationships
    grade = relationship("Grade", back_populates="skills")
    school = relationship("School", back_populates="skills")

    def __repr__(self):
        return f"<Skill(id='{self.id}', name='{self.name}')>"
