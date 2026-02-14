from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .user import UserSchema


class RiderProfileBase(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    date_of_birth: Optional[date] = None


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
