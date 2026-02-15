from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import UserSchema


class RiderProfileBase(BaseModel):
    height_cm: float | None = None
    weight_kg: float | None = None
    date_of_birth: date | None = None


class RiderProfileCreate(RiderProfileBase):
    pass


class RiderProfileSchema(RiderProfileBase):
    id: UUID
    user_id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)


class RiderFullSchema(BaseModel):
    user: UserSchema
    profile: RiderProfileSchema

    model_config = ConfigDict(from_attributes=True)
