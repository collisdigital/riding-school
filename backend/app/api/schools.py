import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.auth_helpers import get_user_permissions, set_access_cookie
from app.db import get_db
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.school import School
from app.models.user import User
from app.schemas.school import SchoolCreate, SchoolSchema

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=SchoolSchema)
def create_school(
    school_in: SchoolCreate,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if current_user.school_id:
        raise HTTPException(
            status_code=400, detail="User already belongs to a school context"
        )

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
        db.flush()  # Get membership.id

        # Assign Role
        mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
        db.add(mem_role)

        db.commit()
        db.refresh(school)

        # Refresh access token so new school context and permissions are available
        school_id, perms, roles = get_user_permissions(db, current_user.id)
        access_token = security.create_access_token(
            current_user.id,
            school_id=school_id,
            perms=perms,
            roles=roles,
        )
        set_access_cookie(response, access_token)

        return school

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create school: {e}")
        raise HTTPException(status_code=500, detail="Failed to create school") from None
