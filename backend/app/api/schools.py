import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import deps
from app.db import get_db
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.school import School
from app.models.user import User
from app.schemas.school import SchoolCreate, SchoolSchema

router = APIRouter()


@router.post("/", response_model=SchoolSchema)
def create_school(
    school_in: SchoolCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    # Check if user already has memberships?
    # For MVP, maybe enforce single-school per user for now?
    # Or just let them create multiple schools?
    # Original logic: `if current_user.school_id: raise...`
    # Since `current_user.school_id` is derived from context, this prevents
    # creating a school while logged into another school context.
    # But if they have NO context (school_id=None), they can create one.
    if current_user.school_id:
        raise HTTPException(status_code=400, detail="User already belongs to a school context")

    slug = school_in.name.lower().replace(" ", "-")
    # Check if slug exists
    if db.query(School).filter(School.slug == slug).first():
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"

    # Transaction
    try:
        # Create School
        school = School(name=school_in.name, slug=slug)
        db.add(school)
        db.flush()  # Get school.id

        # Get Admin Role
        admin_role = db.query(Role).filter(Role.name == Role.ADMIN).first()
        if not admin_role:
            # Seed if missing
            admin_role = Role(name=Role.ADMIN, description="Administrator")
            db.add(admin_role)
            db.flush()

        # Create Membership
        membership = Membership(user_id=current_user.id, school_id=school.id)
        db.add(membership)
        db.flush() # Get membership.id

        # Assign Role
        mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
        db.add(mem_role)

        db.commit()
        db.refresh(school)
        return school

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create school: {str(e)}") from None
