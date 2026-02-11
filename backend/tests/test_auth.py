import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app


@pytest.mark.asyncio
async def test_register_user_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "strongpassword123",
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
        "password": "password123",
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
    password = "secretpassword"

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
