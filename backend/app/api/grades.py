from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.api.deps import RequirePermission, get_db
from app.models.grade import Grade, Skill
from app.schemas.grade import (
    GradeCreate,
    GradeReorder,
    GradeResponse,
    SkillCreate,
    SkillResponse,
)
from app.schemas.token import TokenPayload

router = APIRouter()


@router.get("/", response_model=list[GradeResponse])
def list_grades(
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("grades:view_history")),
):
    """
    List all grades and nested skills for the current school.
    """
    school_id = UUID(token.sid)
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
    school_id = UUID(token.sid)

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
    db.commit()
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
    school_id = UUID(token.sid)

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
    db.commit()
    db.refresh(skill)
    return skill


@router.patch("/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_grades(
    reorder_in: GradeReorder,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Reorder grades based on list of IDs.
    """
    school_id = UUID(token.sid)

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

    db.commit()


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    grade_id: UUID,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(RequirePermission("school:edit_settings")),
):
    """
    Soft delete a grade.
    """
    school_id = UUID(token.sid)
    grade = (
        db.query(Grade)
        .filter(Grade.id == grade_id, Grade.school_id == school_id)
        .first()
    )
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found"
        )

    grade.deleted_at = func.now()
    db.commit()
