import uuid6
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid6.uuid7)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    memberships = relationship(
        "Membership", back_populates="user", cascade="all, delete-orphan"
    )
    rider_profiles = relationship(
        "RiderProfile", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(email='{self.email}')>"
