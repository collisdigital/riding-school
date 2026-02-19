import uuid6
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, TimestampMixin


class School(Base, TimestampMixin):
    __tablename__ = "schools"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    name = Column(String, index=True)  # Removed unique=True
    slug = Column(String, unique=True, index=True)

    memberships = relationship(
        "Membership", back_populates="school", cascade="all, delete-orphan"
    )
    rider_profiles = relationship(
        "RiderProfile", back_populates="school", cascade="all, delete-orphan"
    )
    grades = relationship(
        "Grade", back_populates="school", cascade="all, delete-orphan"
    )
    skills = relationship(
        "Skill", back_populates="school", cascade="all, delete-orphan"
    )
    rider_grade_history = relationship(
        "RiderGradeHistory", back_populates="school", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<School(name='{self.name}')>"
