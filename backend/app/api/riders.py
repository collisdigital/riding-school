import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.api import deps
from app.db import get_db
from app.models.membership import Membership, MembershipRole
from app.models.rider_profile import RiderProfile
from app.models.role import Role
from app.models.user import User
from app.schemas.rider import RiderCreate, RiderResponse, RiderUpdate

router = APIRouter()


@router.post("/", response_model=RiderResponse)
def create_rider(
    rider_in: RiderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    """
    Create a new rider.
    - If email provided, links to existing user or creates new global user.
    - If no email, creates a managed user.
    - Creates Membership and RiderProfile for the current school.
    """
    school_id = current_user.school_id

    # 1. Resolve User
    user = None
    if rider_in.email:
        user = db.query(User).filter(User.email == rider_in.email).first()

    if not user:
        # Create new user
        user = User(
            email=rider_in.email,
            first_name=rider_in.first_name,
            last_name=rider_in.last_name,
            is_active=True,
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

    # 2. Check/Create Membership
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user.id, Membership.school_id == school_id)
        .first()
    )

    if not membership:
        membership = Membership(user_id=user.id, school_id=school_id)
        db.add(membership)
        db.flush()

    # 3. Assign RIDER Role
    rider_role = db.query(Role).filter(Role.name == Role.RIDER).first()
    if not rider_role:
        # Fallback/Seed
        rider_role = Role(name=Role.RIDER, description="Student Rider")
        db.add(rider_role)
        db.flush()

    # Check if role already assigned
    has_role = (
        db.query(MembershipRole)
        .filter(
            MembershipRole.membership_id == membership.id,
            MembershipRole.role_id == rider_role.id,
        )
        .first()
    )
    if not has_role:
        mem_role = MembershipRole(membership_id=membership.id, role_id=rider_role.id)
        db.add(mem_role)

    # 4. Create/Update Rider Profile
    # Check if profile already exists (e.g. re-adding a user)
    profile = (
        db.query(RiderProfile)
        .filter(RiderProfile.user_id == user.id, RiderProfile.school_id == school_id)
        .first()
    )

    if profile:
        # Update existing profile
        profile.height_cm = rider_in.height_cm
        profile.weight_kg = rider_in.weight_kg
        profile.date_of_birth = rider_in.date_of_birth
        # Reactivate if soft deleted?
        if profile.deleted_at:
            profile.deleted_at = None
    else:
        profile = RiderProfile(
            user_id=user.id,
            school_id=school_id,
            height_cm=rider_in.height_cm,
            weight_kg=rider_in.weight_kg,
            date_of_birth=rider_in.date_of_birth,
        )
        db.add(profile)

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create rider: {str(e)}"
        ) from None

    db.refresh(profile)

    # Construct response
    return RiderResponse(
        id=profile.id,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        date_of_birth=profile.date_of_birth,
        school_id=school_id,
    )


@router.get("/", response_model=list[RiderResponse])
def list_riders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    """
    List all riders for the current school.
    Automatically filters soft-deleted profiles via DB event.
    """
    school_id = current_user.school_id

    profiles = (
        db.query(RiderProfile)
        .join(User)
        .filter(RiderProfile.school_id == school_id)
        .all()
    )

    # Map to schema
    results = []
    for p in profiles:
        results.append(
            RiderResponse(
                id=p.id,
                user_id=p.user_id,
                first_name=p.user.first_name,
                last_name=p.user.last_name,
                email=p.user.email,
                height_cm=p.height_cm,
                weight_kg=p.weight_kg,
                date_of_birth=p.date_of_birth,
                school_id=p.school_id,
            )
        )
    return results


@router.get("/{rider_id}", response_model=RiderResponse)
def get_rider(
    rider_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_school_user),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID") from None

    profile = (
        db.query(RiderProfile)
        .join(User)
        .filter(
            RiderProfile.id == r_id, RiderProfile.school_id == current_user.school_id
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Rider not found")

    return RiderResponse(
        id=profile.id,
        user_id=profile.user_id,
        first_name=profile.user.first_name,
        last_name=profile.user.last_name,
        email=profile.user.email,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        date_of_birth=profile.date_of_birth,
        school_id=profile.school_id,
    )


@router.put("/{rider_id}", response_model=RiderResponse)
def update_rider(
    rider_id: str,
    rider_in: RiderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permissions(["riders:update"])),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID") from None

    profile = (
        db.query(RiderProfile)
        .join(User)
        .filter(
            RiderProfile.id == r_id, RiderProfile.school_id == current_user.school_id
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Rider not found")

    # Update User fields if provided
    user = profile.user
    if rider_in.first_name is not None:
        user.first_name = rider_in.first_name
    if rider_in.last_name is not None:
        user.last_name = rider_in.last_name
    if rider_in.email is not None:
        # Check uniqueness if email changed
        if user.email != rider_in.email:
            existing = db.query(User).filter(User.email == rider_in.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already in use")
        user.email = rider_in.email

    # Update Profile fields
    if rider_in.height_cm is not None:
        profile.height_cm = rider_in.height_cm
    if rider_in.weight_kg is not None:
        profile.weight_kg = rider_in.weight_kg
    if rider_in.date_of_birth is not None:
        profile.date_of_birth = rider_in.date_of_birth

    try:
        db.commit()
        db.refresh(profile)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update rider") from None

    return RiderResponse(
        id=profile.id,
        user_id=profile.user_id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        date_of_birth=profile.date_of_birth,
        school_id=profile.school_id,
    )


@router.delete("/{rider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rider(
    rider_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.check_permissions(["riders:delete"])),
):
    try:
        r_id = uuid.UUID(rider_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rider ID") from None

    # Find profile
    profile = (
        db.query(RiderProfile)
        .filter(
            RiderProfile.id == r_id, RiderProfile.school_id == current_user.school_id
        )
        .first()
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Rider not found")

    # Soft delete Profile
    profile.deleted_at = func.now()

    # Soft delete Membership (if exists and exclusive to rider role?)
    # Prompt said: "soft-delete the Rider Profile and the Membership for that school simultaneously"
    membership = (
        db.query(Membership)
        .filter(
            Membership.user_id == profile.user_id,
            Membership.school_id == current_user.school_id,
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
