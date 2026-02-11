from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from uuid import UUID

# RBAC
class PermissionSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class RoleSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionSchema] = []

    model_config = ConfigDict(from_attributes=True)

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

# Properties to return via API
class UserSchema(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    school_id: Optional[UUID] = None
    roles: List[RoleSchema] = []

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
    school: Optional[SchoolSchema] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    school_id: Optional[str] = None
