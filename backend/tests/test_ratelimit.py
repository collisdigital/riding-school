import pytest
from httpx import ASGITransport, AsyncClient

from app.api.auth import login_limiter
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
