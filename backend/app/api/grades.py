from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import RequirePermission, get_db
from app.models.grade import Grade, Skill
from app.models.rider_grade_history import RiderGradeHistory
from app.schemas.grade import (
    GradeCreate,
    GradeReorder,
    GradeResponse,
    SkillCreate,
    SkillResponse,
)
from app.schemas.token import TokenPayload

router = APIRouter()


def _get_school_id(token: TokenPayload) -> UUID:
    if not token.sid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid school context"
        )
    return UUID(token.sid)


@router.get("/", response_model=list[GradeResponse])
def list_grades(
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("grades:view_history")),
):
    """
    List all grades and nested skills for the current school.
    """
    school_id = _get_school_id(token)
    grades = (
        db.query(Grade)
        .options(selectinload(Grade.skills))
        .filter(Grade.school_id == school_id)
        .order_by(Grade.sequence_order)
        .all()
    )
    return grades


@router.post("/", response_model=GradeResponse)
def create_grade(
    grade_in: GradeCreate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Create a new Grade.
    """
    school_id = _get_school_id(token)

    # Calculate next sequence_order
    max_order = (
        db.query(func.max(Grade.sequence_order))
        .filter(Grade.school_id == school_id)
        .scalar()
    )
    next_order = (max_order if max_order is not None else -1) + 1

    grade = Grade(
        name=grade_in.name,
        description=grade_in.description,
        sequence_order=next_order,
        school_id=school_id,
    )
    db.add(grade)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create grade",
        ) from None
    db.refresh(grade)
    return grade


@router.post("/{grade_id}/skills", response_model=SkillResponse)
def add_skill(
    grade_id: UUID,
    skill_in: SkillCreate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Add a skill to a grade.
    """
    school_id = _get_school_id(token)

    # Verify grade exists and belongs to school
    grade = (
        db.query(Grade)
        .filter(Grade.id == grade_id, Grade.school_id == school_id)
        .first()
    )
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found"
        )

    skill = Skill(
        name=skill_in.name,
        description=skill_in.description,
        grade_id=grade_id,
        school_id=school_id,
    )
    db.add(skill)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create skill",
        ) from None
    db.refresh(skill)
    return skill


@router.put("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: UUID,
    skill_in: SkillCreate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Update a skill.
    """
    school_id = _get_school_id(token)

    skill = (
        db.query(Skill)
        .filter(Skill.id == skill_id, Skill.school_id == school_id)
        .first()
    )
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )

    skill.name = skill_in.name
    skill.description = skill_in.description

    try:
        db.commit()
        db.refresh(skill)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update skill",
        ) from None
    return skill


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Delete a skill.
    """
    school_id = _get_school_id(token)

    skill = (
        db.query(Skill)
        .filter(Skill.id == skill_id, Skill.school_id == school_id)
        .first()
    )
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found"
        )

    # Soft delete
    skill.deleted_at = func.now()
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete skill",
        ) from None


@router.patch("/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_grades(
    reorder_in: GradeReorder,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Reorder grades based on list of IDs.
    """
    school_id = _get_school_id(token)

    # Fetch all grades for school
    grades = (
        db.query(Grade)
        .filter(Grade.school_id == school_id)
        .filter(Grade.id.in_(reorder_in.ordered_ids))
        .all()
    )

    grade_map = {g.id: g for g in grades}

    # Update sequence_order
    for index, grade_id in enumerate(reorder_in.ordered_ids):
        if grade_id in grade_map:
            grade_map[grade_id].sequence_order = index

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder grades",
        ) from None


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    grade_id: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Soft delete a grade.
    Prevents deletion if the grade has rider history records.
    """
    school_id = _get_school_id(token)
    grade = (
        db.query(Grade)
        .filter(Grade.id == grade_id, Grade.school_id == school_id)
        .first()
    )
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found"
        )

    # Check for usage in rider history (completed or active)
    has_history = (
        db.query(RiderGradeHistory)
        .filter(RiderGradeHistory.grade_id == grade_id)
        .first()
    )
    if has_history:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete grade referenced by rider history records.",
        )

    grade.deleted_at = func.now()
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete grade",
        ) from None
