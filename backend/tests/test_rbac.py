import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.school import School
from app.models.user import User


@pytest.mark.asyncio
async def test_instructor_cannot_delete_rider(db_session):
    # 1. Setup: Create School
    school = School(name="Test School", slug=f"test-school-{uuid.uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    # 2. Setup: Create an Instructor user
    email = "instructor@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Instructor",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    instructor_role = (
        db_session.query(Role).filter(Role.name == Role.INSTRUCTOR).first()
    )
    if not instructor_role:
        instructor_role = Role(name=Role.INSTRUCTOR)
        db_session.add(instructor_role)
        db_session.flush()

    mem_role = MembershipRole(membership_id=membership.id, role_id=instructor_role.id)
    db_session.add(mem_role)

    db_session.commit()

    # 3. Login to get token
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 4. Try to delete a (non-existent) rider to check permission
        # Even if the rider doesn't exist, the permission check happens first.
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403
    # The message is hardcoded in deps.py
    assert "Missing required permission: riders:delete" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_can_delete_rider(db_session):
    # 1. Setup: Create School
    school = School(name="Admin School", slug=f"admin-school-{uuid.uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    # 2. Setup: Create an Admin user
    email = "admin@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    if not admin_role:
        admin_role = Role(name=Role.ADMIN)
        db_session.add(admin_role)
        db_session.flush()

    mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
    db_session.add(mem_role)

    db_session.commit()

    # 3. Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 4. Try to delete - should get 404 (not found) instead of 403 (forbidden)
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 404  # Permission passed, but rider not found
