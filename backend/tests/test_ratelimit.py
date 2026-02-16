import pytest
from httpx import ASGITransport, AsyncClient

from app.api.auth import login_limiter, register_limiter
from app.main import app


@pytest.mark.asyncio
async def test_rate_limiter_blocks_excessive_requests():
    # Clear the limiter state before test
    login_limiter.requests.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Make 5 allowed requests
        for _ in range(5):
            response = await ac.post(
                "/api/auth/login",
                data={"username": "test@example.com", "password": "wrongpassword"},
            )
            # Expect 400 (Bad Request) due to invalid credentials, NOT 429
            assert response.status_code == 400

        # Make the 6th request
        response = await ac.post(
            "/api/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )
        # Expect 429 Too Many Requests
        assert response.status_code == 429
        assert (
            response.json()["detail"]
            == "Too many login attempts. Please try again later."
        )

    # Cleanup
    login_limiter.requests.clear()


@pytest.mark.asyncio
async def test_register_rate_limiter():
    # Clear the limiter state before test
    register_limiter.requests.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "email": "rate@example.com",
            "password": "StrongPass1!",
            "first_name": "Rate",
            "last_name": "Test",
        }
        # Make 5 allowed requests
        for i in range(5):
            # Use unique emails to avoid 400 error from duplicate user
            p = payload.copy()
            p["email"] = f"rate{i}@example.com"
            response = await ac.post("/api/auth/register", json=p)
            assert response.status_code == 200

        # Make the 6th request
        p = payload.copy()
        p["email"] = "rate_limit@example.com"
        response = await ac.post("/api/auth/register", json=p)

        # Expect 429 Too Many Requests
        assert response.status_code == 429
        assert (
            response.json()["detail"]
            == "Too many registration attempts. Please try again later."
        )

    # Cleanup
    register_limiter.requests.clear()
