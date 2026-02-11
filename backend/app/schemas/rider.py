from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class RiderBase(BaseModel):
    first_name: str
    last_name: str

class RiderCreate(RiderBase):
    pass

class RiderSchema(RiderBase):
    id: UUID
    school_id: UUID

    class Config:
        from_attributes = True
