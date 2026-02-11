import uuid

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid

from .base import Base, TimestampMixin


class School(Base, TimestampMixin):
    __tablename__ = "schools"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="school")

    def __repr__(self):
        return f"<School(name='{self.name}')>"
