import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core import security
from app.core.config import settings
from app.main import app
from app.models.membership import Membership
from app.models.school import School
from app.models.user import User


@pytest.mark.asyncio
async def test_create_school_success(db_session):
    # 1. Setup: Create a user without a school
    email = "noschool@example.com"
    password = "password123"
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        first_name="No",
        last_name="School",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 2. Login
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 3. Create School
        response = await ac.post(
            "/api/schools/",
            json={"name": "New School"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "New School"
    assert "slug" in data
    assert data["slug"] == "new-school"


@pytest.mark.asyncio
async def test_create_school_already_has_one(db_session):
    # 1. Setup: Create a user with a school
    school = School(name="Existing", slug="existing")
    db_session.add(school)
    db_session.flush()

    email = "hasschool@example.com"
    password = "password123"
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        first_name="Has",
        last_name="School",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        response = await ac.post(
            "/api/schools/",
            json={"name": "Another School"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already belongs to a school context"


@pytest.mark.asyncio
async def test_create_school_duplicate_slug(db_session):
    # Setup two users
    email1 = "user1@example.com"
    email2 = "user2@example.com"
    password = "password123"
    u1 = User(
        email=email1,
        hashed_password=security.get_password_hash(password),
        first_name="U1",
        last_name="T",
        is_active=True,
    )
    u2 = User(
        email=email2,
        hashed_password=security.get_password_hash(password),
        first_name="U2",
        last_name="T",
        is_active=True,
    )
    db_session.add_all([u1, u2])
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # User 1 creates "Willow Creek"
        login1 = await ac.post(
            "/api/auth/login", data={"username": email1, "password": password}
        )
        token1 = login1.json()["access_token"]

        # User 1 has no school yet, so they can create one
        resp1 = await ac.post(
            "/api/schools/",
            json={"name": "Willow Creek"},
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert resp1.status_code == 200

        # User 2 creates "Willow Creek"
        login2 = await ac.post(
            "/api/auth/login", data={"username": email2, "password": password}
        )
        token2 = login2.json()["access_token"]
        response = await ac.post(
            "/api/schools/",
            json={"name": "Willow Creek"},
            headers={"Authorization": f"Bearer {token2}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["slug"].startswith("willow-creek-")
    assert len(data["slug"]) > len("willow-creek")


@pytest.mark.asyncio
async def test_create_school_refreshes_access_token_claims(db_session):
    email = "refresh-claims@example.com"
    password = "password123"
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        first_name="Refresh",
        last_name="Claims",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        assert login_res.status_code == 200

        create_res = await ac.post("/api/schools/", json={"name": "Token School"})
        assert create_res.status_code == 200

        access_cookie = create_res.cookies.get("access_token")
        assert access_cookie is not None

        claims = jwt.decode(
            access_cookie, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert claims.get("sid") is not None
        assert "riders:view" in claims.get("perms", [])

        riders_res = await ac.get("/api/riders/")
        assert riders_res.status_code == 200
        assert riders_res.json() == []
