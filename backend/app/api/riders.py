from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
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
    rider = db.query(Rider).filter(
        Rider.id == rider_id,
        Rider.school_id == current_user.school_id # CRITICAL: Multi-tenant filter
    ).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return rider
