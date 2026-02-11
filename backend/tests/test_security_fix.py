import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_login_sets_cookie():
    payload = {
        "username": "test@example.com",
        "password": "strongpassword123",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # First register
        await ac.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "strongpassword123",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        # Then login
        response = await ac.post("/api/auth/login", data=payload)

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert response.cookies.get("access_token") is not None
    # Check for HttpOnly (httpx might not show all attributes in cookies dict
    # easily but we can check headers)
    set_cookie = response.headers.get("set-cookie")
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie


@pytest.mark.asyncio
async def test_get_me_with_cookie():
    payload = {
        "username": "cookie@example.com",
        "password": "password123",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register
        await ac.post(
            "/api/auth/register",
            json={
                "email": "cookie@example.com",
                "password": "password123",
                "first_name": "Cookie",
                "last_name": "User",
            },
        )

        # Login to get cookie
        login_res = await ac.post("/api/auth/login", data=payload)
        assert "access_token" in login_res.cookies

        # Use cookie for /me
        response = await ac.get("/api/auth/me", cookies=login_res.cookies)

    assert response.status_code == 200
    assert response.json()["email"] == "cookie@example.com"


@pytest.mark.asyncio
async def test_logout_clears_cookie():
    payload = {
        "username": "logout@example.com",
        "password": "password123",
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register
        await ac.post(
            "/api/auth/register",
            json={
                "email": "logout@example.com",
                "password": "password123",
                "first_name": "Logout",
                "last_name": "User",
            },
        )

        # Login
        login_res = await ac.post("/api/auth/login", data=payload)

        # Logout
        logout_res = await ac.post("/api/auth/logout", cookies=login_res.cookies)
        assert logout_res.status_code == 200

        # Check if cookie is cleared (Max-Age=0 or Expires in the past)
        set_cookie = logout_res.headers.get("set-cookie")
        assert 'access_token=""' in set_cookie or "access_token=;" in set_cookie
        assert (
            "Max-Age=0" in set_cookie
            or "expires=Thu, 01 Jan 1970 00:00:00 GMT" in set_cookie
        )
