from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app
from app.models.membership import Membership
from app.models.school import School
from app.models.user import User


@pytest.mark.asyncio
async def test_login_issue_refresh_token(db_session):
    # Setup User
    password = "StrongPass1!"
    user = User(
        email="refresh@example.com",
        hashed_password=security.get_password_hash(password),
        first_name="Refresh",
        last_name="Test",
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    # Create School/Membership to avoid "No school context" issues if stricter checks
    # added later. Though login works without membership (defaults to None school_id)
    school = School(name="Refresh School", slug=f"refresh-{uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.commit()

    # Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/login",
            data={"username": user.email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

    assert response.status_code == 200
    cookies = response.cookies
    assert "refresh_token" in cookies
    assert "access_token" in cookies

    rt = cookies["refresh_token"]

    # Test Refresh
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.cookies.set("refresh_token", rt)
        response_refresh = await ac.post("/api/auth/refresh")

    assert response_refresh.status_code == 200
    new_cookies = response_refresh.cookies
    assert "refresh_token" in new_cookies
    assert "access_token" in new_cookies

    new_rt = new_cookies["refresh_token"]
    assert new_rt != rt

    # Test Old Refresh Token Revocation (Reuse Attempt)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.cookies.set("refresh_token", rt)
        response_reuse = await ac.post("/api/auth/refresh")

    assert response_reuse.status_code == 401

    # Test Logout
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.cookies.set("refresh_token", new_rt)
        response_logout = await ac.post("/api/auth/logout")

    assert response_logout.status_code == 200
    # Check if cookie is cleared (value is empty or Expires in past)
    # httpx handles cookies clearing by setting value to empty string usually
    # But response.cookies might just have the Set-Cookie header.
    # Let's verify we can't use it anymore.

    # Verify logout revoked token
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ac.cookies.set("refresh_token", new_rt)
        response_revoked = await ac.post("/api/auth/refresh")

    assert response_revoked.status_code == 401
