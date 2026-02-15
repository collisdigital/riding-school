from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)

    roles = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission(name='{self.name}')>"
