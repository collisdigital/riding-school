from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import UserSchema


class RoleSchema(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MembershipBase(BaseModel):
    user_id: UUID
    school_id: UUID


class MembershipCreate(MembershipBase):
    role_ids: list[int]


class MembershipSchema(MembershipBase):
    id: UUID
    roles: list[RoleSchema] = []
    user: UserSchema | None = None

    model_config = ConfigDict(from_attributes=True)
