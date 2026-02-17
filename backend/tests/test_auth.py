from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.school import School
from app.models.user import User


@pytest.mark.asyncio
async def test_register_user_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "StrongPass1!",
                "first_name": "Test",
                "last_name": "User",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email():
    payload = {
        "email": "dup@example.com",
        "password": "StrongPass1!",
        "first_name": "Dup",
        "last_name": "User",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/auth/register", json=payload)
        response = await ac.post("/api/auth/register", json=payload)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The user with this email already exists in the system."
    )


@pytest.mark.asyncio
async def test_password_is_hashed(db_session):
    from app.models.user import User

    email = "hashed@example.com"
    password = "StrongPass1!"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": password,
                "first_name": "Hash",
                "last_name": "Test",
            },
        )

    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.hashed_password != password
    assert security.verify_password(password, user.hashed_password)


@pytest.mark.asyncio
async def test_get_me_success(db_session):
    # 1. Create a school and a user
    school = School(name="Test School", slug=f"test-school-{uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    user = User(
        email="me@example.com",
        hashed_password=security.get_password_hash("password123"),
        first_name="Me",
        last_name="Test",
    )
    db_session.add(user)
    db_session.flush()

    # Create Membership
    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    # Assign Role? Not strictly needed for get_me but good practice
    role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    if not role:
        role = Role(name=Role.ADMIN)
        db_session.add(role)
        db_session.flush()

    mem_role = MembershipRole(membership_id=membership.id, role_id=role.id)
    db_session.add(mem_role)

    db_session.commit()

    # 2. Get token
    token = security.create_access_token(user.id, school_id=school.id)

    # 3. Call /me
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["school"]["name"] == "Test School"


@pytest.mark.asyncio
async def test_register_weak_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",
                "first_name": "Weak",
                "last_name": "Pass",
            },
        )
    # Expect 422 Unprocessable Entity because validation should fail
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_me_invalid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "Could not validate credentials"
