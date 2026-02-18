from datetime import date
from uuid import UUID

from pydantic import AliasPath, BaseModel, ConfigDict, EmailStr, Field


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


class RiderGradeUpdate(BaseModel):
    grade_id: UUID


class RiderResponse(BaseModel):
    id: UUID  # RiderProfile ID
    user_id: UUID
    first_name: str = Field(validation_alias=AliasPath("user", "first_name"))
    last_name: str = Field(validation_alias=AliasPath("user", "last_name"))
    email: str | None = Field(None, validation_alias=AliasPath("user", "email"))
    height_cm: float | None = None
    weight_kg: float | None = None
    date_of_birth: date | None = None
    school_id: UUID

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
