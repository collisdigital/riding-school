import uuid
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    OWNER = "OWNER"
    INSTRUCTOR = "INSTRUCTOR"
    RIDER = "RIDER"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.RIDER)
    
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=True)
    school = relationship("School", back_populates="users")

    def __repr__(self):
        return f"<User(email='{self.email}')>"
