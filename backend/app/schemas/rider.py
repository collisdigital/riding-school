from typing import List, Optional
from datetime import date
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class RiderCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    date_of_birth: Optional[date] = None


class RiderUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    date_of_birth: Optional[date] = None


class RiderResponse(BaseModel):
    id: UUID  # RiderProfile ID
    user_id: UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    date_of_birth: Optional[date] = None
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)
