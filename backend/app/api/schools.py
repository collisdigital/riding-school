import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db import get_db
from app.models.rbac import Role
from app.models.school import School
from app.models.user import User
from app.schemas import SchoolCreate, SchoolSchema

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

    db_obj = School(name=school_in.name, slug=slug)
    db.add(db_obj)
    db.flush()  # Get the ID

    current_user.school_id = db_obj.id

    # Assign Admin role
    admin_role = db.query(Role).filter(Role.name == "Admin").first()
    if not admin_role:
        # Fallback if roles aren't seeded yet
        admin_role = Role(name="Admin")
        db.add(admin_role)
        db.flush()

    if admin_role not in current_user.roles:
        current_user.roles.append(admin_role)

    db.commit()
    db.refresh(db_obj)
    return db_obj
