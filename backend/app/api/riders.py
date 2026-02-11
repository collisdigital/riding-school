from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from app.db import get_db
from app.api import deps
from app.models.user import User
from app.models.rider import Rider
from app.schemas.rider import RiderCreate, RiderSchema

router = APIRouter()

@router.post("/", response_model=RiderSchema)
def create_rider(
    rider_in: RiderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    db_obj = Rider(
        **rider_in.model_dump(),
        school_id=current_user.school_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[RiderSchema])
def list_riders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    # CRITICAL: Multi-tenant filter
    return db.query(Rider).filter(Rider.school_id == current_user.school_id).all()

@router.get("/{rider_id}", response_model=RiderSchema)
def get_rider(
    rider_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID")

    rider = db.query(Rider).filter(
        Rider.id == r_id,
        Rider.school_id == current_user.school_id # CRITICAL: Multi-tenant filter
    ).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return rider

@router.delete("/{rider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rider(
    rider_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permissions(["riders:delete"])),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID")

    rider = db.query(Rider).filter(
        Rider.id == r_id,
        Rider.school_id == current_user.school_id
    ).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    db.delete(rider)
    db.commit()
    return None
