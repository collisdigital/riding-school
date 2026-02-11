from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RiderBase(BaseModel):
    first_name: str
    last_name: str


class RiderCreate(RiderBase):
    pass


class RiderSchema(RiderBase):
    id: UUID
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)
