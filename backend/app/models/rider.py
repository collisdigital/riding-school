import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin, TenantMixin

class Rider(Base, TimestampMixin, TenantMixin):
    __tablename__ = "riders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<Rider(name='{self.first_name} {self.last_name}')>"
