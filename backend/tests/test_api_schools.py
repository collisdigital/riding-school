import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.core import security

@pytest.mark.asyncio
async def test_create_school_success(db_session):
    # 1. Setup: Create a user without a school
    email = "noschool@example.com"
    password = "password123"
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        first_name="No",
        last_name="School"
    )
    db_session.add(user)
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 2. Login
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 3. Create School
        response = await ac.post(
            "/api/schools/",
            json={"name": "New School"},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New School"
    assert "slug" in data
    assert data["slug"] == "new-school"

@pytest.mark.asyncio
async def test_create_school_already_has_one(db_session):
    # 1. Setup: Create a user with a school
    from app.models.school import School
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
        school_id=school.id
    )
    db_session.add(user)
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        response = await ac.post(
            "/api/schools/",
            json={"name": "Another School"},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "User already belongs to a school"

@pytest.mark.asyncio
async def test_create_school_duplicate_slug(db_session):
    # Setup two users
    email1 = "user1@example.com"
    email2 = "user2@example.com"
    password = "password123"
    u1 = User(email=email1, hashed_password=security.get_password_hash(password), first_name="U1", last_name="T")
    u2 = User(email=email2, hashed_password=security.get_password_hash(password), first_name="U2", last_name="T")
    db_session.add_all([u1, u2])
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # User 1 creates "Willow Creek"
        login1 = await ac.post("/api/auth/login", data={"username": email1, "password": password})
        token1 = login1.json()["access_token"]
        await ac.post("/api/schools/", json={"name": "Willow Creek"}, headers={"Authorization": f"Bearer {token1}"})

        # User 2 creates "Willow Creek"
        login2 = await ac.post("/api/auth/login", data={"username": email2, "password": password})
        token2 = login2.json()["access_token"]
        response = await ac.post("/api/schools/", json={"name": "Willow Creek"}, headers={"Authorization": f"Bearer {token2}"})

    assert response.status_code == 200
    data = response.json()
    assert data["slug"].startswith("willow-creek-")
    assert len(data["slug"]) > len("willow-creek")
