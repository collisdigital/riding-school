from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class RiderCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    date_of_birth: date | None = None


class RiderUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    date_of_birth: date | None = None


class RiderResponse(BaseModel):
    id: UUID  # RiderProfile ID
    user_id: UUID
    first_name: str
    last_name: str
    email: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    date_of_birth: date | None = None
    school_id: UUID

    model_config = ConfigDict(from_attributes=True)
