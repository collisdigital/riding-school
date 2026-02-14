from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    # Static roles
    ADMIN = "ADMIN"
    INSTRUCTOR = "INSTRUCTOR"
    PARENT = "PARENT"
    RIDER = "RIDER"

    membership_roles = relationship("MembershipRole", back_populates="role")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"
