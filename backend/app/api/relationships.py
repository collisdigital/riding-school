from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, contains_eager, selectinload

from app.api import deps
from app.db import get_db
from app.models.rbac import Relationship, Role
from app.models.user import User
from app.schemas import UserSchema

router = APIRouter()


@router.get("/children", response_model=list[UserSchema])
def get_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    # Fetch all riders linked to this parent
    # Bolt: Eager load rider, roles, and permissions to avoid N+1 query problem
    relationships = (
        db.query(Relationship)
        .join(User, Relationship.rider)
        .options(
            contains_eager(Relationship.rider)
            .selectinload(User.roles)
            .selectinload(Role.permissions)
        )
        .filter(
            Relationship.parent_id == current_user.id,
            User.school_id == current_user.school_id,
        )
        .all()
    )
    children = [rel.rider for rel in relationships]
    return children


@router.post("/link-child/{child_id}", status_code=status.HTTP_201_CREATED)
def link_child(
    child_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    import uuid

    try:
        c_id = uuid.UUID(child_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid child ID") from None

    # Check if child exists and belongs to the same school
    child = (
        db.query(User)
        .filter(User.id == c_id, User.school_id == current_user.school_id)
        .first()
    )
    if not child:
        raise HTTPException(status_code=404, detail="Child not found in your school")

    # Check if already linked
    existing = (
        db.query(Relationship)
        .filter(
            Relationship.parent_id == current_user.id, Relationship.rider_id == c_id
        )
        .first()
    )

    if existing:
        return {"message": "Already linked"}

    rel = Relationship(parent_id=current_user.id, rider_id=c_id)
    db.add(rel)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to link child") from None
    return {"message": "Child linked successfully"}
