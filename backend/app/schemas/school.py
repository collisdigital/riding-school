from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SchoolBase(BaseModel):
    name: str


class SchoolCreate(SchoolBase):
    pass


class SchoolSchema(SchoolBase):
    id: UUID
    slug: str

    model_config = ConfigDict(from_attributes=True)
