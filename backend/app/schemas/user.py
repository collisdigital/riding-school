from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class SchoolSimple(BaseModel):
    id: UUID
    name: str
    slug: str
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserSchema(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


class UserWithSchool(UserSchema):
    school: SchoolSimple | None = None

    # Return list of role names
    roles: list[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator("roles", mode="before")
    @classmethod
    def parse_roles(cls, v: Any) -> list[str]:
        if not v:
            return []
        # If it's a list of Role objects, extract name
        # If it's already strings, keep them
        res = []
        for item in v:
            if hasattr(item, "name"):
                res.append(item.name)
            else:
                res.append(str(item))
        return res
