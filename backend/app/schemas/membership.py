from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import UserSchema


class RoleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MembershipBase(BaseModel):
    user_id: UUID
    school_id: UUID


class MembershipCreate(MembershipBase):
    role_ids: List[int]


class MembershipSchema(MembershipBase):
    id: UUID
    roles: List[RoleSchema] = []
    user: Optional[UserSchema] = None

    model_config = ConfigDict(from_attributes=True)
