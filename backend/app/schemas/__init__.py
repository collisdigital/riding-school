import re
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


# RBAC
class PermissionSchema(BaseModel):
    id: UUID
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RoleSchema(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    permissions: list[PermissionSchema] = []

    model_config = ConfigDict(from_attributes=True)


# Shared properties
class UserBase(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


# Properties to return via API
class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    school_id: UUID | None = None
    roles: list[RoleSchema] = []

    model_config = ConfigDict(from_attributes=True)


class SchoolBase(BaseModel):
    name: str


class SchoolCreate(SchoolBase):
    pass


class SchoolSchema(SchoolBase):
    id: UUID
    slug: str

    model_config = ConfigDict(from_attributes=True)


class UserWithSchool(UserSchema):
    school: SchoolSchema | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: str | None = None
    school_id: str | None = None
