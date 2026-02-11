from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.api import deps
from app.models.school import School
from app.models.user import User, UserRole
from app.schemas import SchoolCreate, SchoolSchema
import uuid

router = APIRouter()

@router.post("/", response_model=SchoolSchema)
def create_school(
    school_in: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.school_id:
        raise HTTPException(status_code=400, detail="User already belongs to a school")
    
    slug = school_in.name.lower().replace(" ", "-")
    # Check if slug exists
    if db.query(School).filter(School.slug == slug).first():
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    db_obj = School(
        name=school_in.name,
        slug=slug
    )
    db.add(db_obj)
    db.flush() # Get the ID
    
    current_user.school_id = db_obj.id
    current_user.role = UserRole.OWNER
    
    db.commit()
    db.refresh(db_obj)
    return db_obj
