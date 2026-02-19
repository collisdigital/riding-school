from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str
    description: str | None = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: UUID
    grade_id: UUID

    model_config = ConfigDict(from_attributes=True)


class GradeBase(BaseModel):
    name: str
    description: str | None = None


class GradeCreate(GradeBase):
    pass


class GradeResponse(GradeBase):
    id: UUID
    sequence_order: int
    skills: list[SkillResponse] = []

    model_config = ConfigDict(from_attributes=True)


class GradeReorder(BaseModel):
    ordered_ids: list[UUID]
