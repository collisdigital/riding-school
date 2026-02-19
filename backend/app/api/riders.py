import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func

from app.api import deps
from app.db import get_db
from app.models.grade import Grade
from app.models.membership import Membership, MembershipRole
from app.models.rider_grade_history import RiderGradeHistory
from app.models.rider_profile import RiderProfile
from app.models.role import Role
from app.models.user import User
from app.schemas.rider import RiderCreate, RiderGradeUpdate, RiderResponse, RiderUpdate
from app.schemas.token import TokenPayload

router = APIRouter()
logger = logging.getLogger(__name__)


def _resolve_user(db: Session, rider_in: RiderCreate) -> User:
    """Find existing user by email or create a new one."""
    user = None
    if rider_in.email:
        user = db.query(User).filter(User.email == rider_in.email).first()

    if not user:
        user = User(
            email=rider_in.email,
            first_name=rider_in.first_name,
            last_name=rider_in.last_name,
            hashed_password=None,  # Managed or Invited later
        )
        db.add(user)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400, detail="User with this email already exists"
            ) from None
    return user


def _ensure_membership(
    db: Session, user_id: uuid.UUID, school_id: uuid.UUID
) -> Membership:
    """Ensure user has membership in the school."""
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user_id, Membership.school_id == school_id)
        .first()
    )
    if not membership:
        membership = Membership(user_id=user_id, school_id=school_id)
        db.add(membership)
        db.flush()
    return membership


def _assign_rider_role(db: Session, membership_id: uuid.UUID) -> None:
    """Ensure membership has the RIDER role."""
    # Get Rider Role ID (Optimized with Cache)
    rider_role_id = Role.get_id(db, Role.RIDER)
    if not rider_role_id:
        # Fallback Seed if missing
        rider_role = Role(name=Role.RIDER, description="Student Rider")
        db.add(rider_role)
        db.flush()
        rider_role_id = rider_role.id
        Role.stage_cache_update(db, Role.RIDER, rider_role_id)

    has_role = (
        db.query(MembershipRole)
        .filter(
            MembershipRole.membership_id == membership_id,
            MembershipRole.role_id == rider_role_id,
        )
        .first()
    )
    if not has_role:
        mem_role = MembershipRole(membership_id=membership_id, role_id=rider_role_id)
        db.add(mem_role)


def _upsert_rider_profile(
    db: Session, user_id: uuid.UUID, school_id: uuid.UUID, rider_in: RiderCreate
) -> RiderProfile:
    """Create or update rider profile."""
    profile = (
        db.query(RiderProfile)
        .filter(RiderProfile.user_id == user_id, RiderProfile.school_id == school_id)
        .first()
    )

    if profile:
        profile.height_cm = rider_in.height_cm
        profile.weight_kg = rider_in.weight_kg
        profile.date_of_birth = rider_in.date_of_birth
        if profile.deleted_at:
            profile.deleted_at = None
    else:
        profile = RiderProfile(
            user_id=user_id,
            school_id=school_id,
            height_cm=rider_in.height_cm,
            weight_kg=rider_in.weight_kg,
            date_of_birth=rider_in.date_of_birth,
        )
        db.add(profile)
    return profile


@router.post("/", response_model=RiderResponse)
def create_rider(
    rider_in: RiderCreate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(deps.RequirePermission("riders:create")),
):
    """
    Create a new rider.
    - If email provided, links to existing user or creates new global user.
    - If no email, creates a managed user.
    - Creates Membership and RiderProfile for the current school.
    """
    if not token.sid:
        raise HTTPException(status_code=400, detail="Invalid school context")
    school_id = uuid.UUID(token.sid)

    # 1. Resolve User
    user = _resolve_user(db, rider_in)

    # 2. Check/Create Membership
    membership = _ensure_membership(db, user.id, school_id)

    # 3. Assign RIDER Role
    _assign_rider_role(db, membership.id)

    # 4. Create/Update Rider Profile
    profile = _upsert_rider_profile(db, user.id, school_id, rider_in)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create rider: {e}")
        raise HTTPException(status_code=500, detail="Failed to create rider") from None

    db.refresh(profile)
    return profile


@router.get("/", response_model=list[RiderResponse])
def list_riders(
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(deps.RequirePermission("riders:view")),
):
    """
    List all riders for the current school.
    Automatically filters soft-deleted profiles via DB event.
    """
    if not token.sid:
        raise HTTPException(status_code=400, detail="Invalid school context")
    school_id = uuid.UUID(token.sid)

    # Bolt: Optimized to fetch user data in same query (avoids N+1)
    profiles = (
        db.query(RiderProfile)
        .options(joinedload(RiderProfile.user))
        .filter(RiderProfile.school_id == school_id)
        .all()
    )

    return profiles


@router.get("/{rider_id}", response_model=RiderResponse)
def get_rider(
    rider_id: str,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(deps.RequirePermission("riders:view")),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID") from None

    if not token.sid:
        raise HTTPException(status_code=400, detail="Invalid school context")
    school_id = uuid.UUID(token.sid)

    profile = (
        db.query(RiderProfile)
        .options(joinedload(RiderProfile.user))
        .filter(RiderProfile.id == r_id, RiderProfile.school_id == school_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Rider not found")

    return profile


def _update_user_fields(db: Session, user: User, rider_in: RiderUpdate) -> None:
    if rider_in.first_name is not None:
        user.first_name = rider_in.first_name
    if rider_in.last_name is not None:
        user.last_name = rider_in.last_name
    if rider_in.email is not None and user.email != rider_in.email:
        existing = db.query(User).filter(User.email == rider_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = rider_in.email


def _update_profile_fields(profile: RiderProfile, rider_in: RiderUpdate) -> None:
    if rider_in.height_cm is not None:
        profile.height_cm = rider_in.height_cm
    if rider_in.weight_kg is not None:
        profile.weight_kg = rider_in.weight_kg
    if rider_in.date_of_birth is not None:
        profile.date_of_birth = rider_in.date_of_birth


@router.put("/{rider_id}", response_model=RiderResponse)
def update_rider(
    rider_id: str,
    rider_in: RiderUpdate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(deps.RequirePermission("riders:update")),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID") from None

    if not token.sid:
        raise HTTPException(status_code=400, detail="Invalid school context")
    school_id = uuid.UUID(token.sid)

    profile = (
        db.query(RiderProfile)
        .options(joinedload(RiderProfile.user))
        .filter(RiderProfile.id == r_id, RiderProfile.school_id == school_id)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Rider not found")

    _update_user_fields(db, profile.user, rider_in)
    _update_profile_fields(profile, rider_in)

    try:
        db.commit()
        db.refresh(profile)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update rider") from None

    return profile


@router.delete("/{rider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rider(
    rider_id: str,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(deps.RequirePermission("riders:delete")),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID") from None

    if not token.sid:
        raise HTTPException(status_code=400, detail="Invalid school context")
    school_id = uuid.UUID(token.sid)

    # Find profile
    profile = (
        db.query(RiderProfile)
        .filter(RiderProfile.id == r_id, RiderProfile.school_id == school_id)
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Rider not found")

    # Soft delete Profile
    profile.deleted_at = func.now()

    # Soft delete Membership (if exists and exclusive to rider role?)
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == profile.user_id,
            Membership.school_id == school_id,
        )
        .first()
    )
    if membership:
        membership.deleted_at = func.now()

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete rider") from None

    return None


@router.patch("/{rider_id}/grade", status_code=status.HTTP_204_NO_CONTENT)
def update_rider_grade(
    rider_id: uuid.UUID,
    grade_update: RiderGradeUpdate,
    db: Session = Depends(get_db),
    token: TokenPayload = Depends(deps.RequirePermission("grades:signoff")),
):
    """
    Update a rider's current grade.
    Marks the previous active grade history as completed and starts a new one.
    """
    if not token.sid:
        raise HTTPException(status_code=400, detail="Invalid school context")
    school_id = uuid.UUID(token.sid)

    # 1. Verify Rider exists
    rider = (
        db.query(RiderProfile)
        .filter(RiderProfile.id == rider_id, RiderProfile.school_id == school_id)
        .first()
    )
    if not rider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rider not found"
        )

    # 2. Verify Grade exists
    grade = (
        db.query(Grade)
        .filter(Grade.id == grade_update.grade_id, Grade.school_id == school_id)
        .first()
    )
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Grade not found"
        )

    # 3. Find current active history and complete it
    current_history = (
        db.query(RiderGradeHistory)
        .filter(
            RiderGradeHistory.rider_id == rider_id,
            RiderGradeHistory.school_id == school_id,
            RiderGradeHistory.completed_at.is_(None),
        )
        .first()
    )

    if current_history:
        # If moving to the same grade, no-op
        if current_history.grade_id == grade_update.grade_id:
            return

        current_history.completed_at = func.now()

    # 4. Create new history
    new_history = RiderGradeHistory(
        rider_id=rider_id,
        grade_id=grade_update.grade_id,
        school_id=school_id,
    )
    db.add(new_history)
    db.commit()
