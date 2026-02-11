import uuid

from sqlalchemy import Column, String
from sqlalchemy.types import Uuid

from .base import Base, TenantMixin, TimestampMixin


class Rider(Base, TimestampMixin, TenantMixin):
    __tablename__ = "riders"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Rider(name='{self.first_name} {self.last_name}')>"
