import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.models.school import School
from app.core import security

@pytest.mark.asyncio
async def test_parent_child_linking(db_session):
    # 1. Setup: School, Parent, Child
    school = School(name="Family School", slug="family")
    db_session.add(school)
    db_session.flush()

    pw = security.get_password_hash("password123")
    parent = User(email="parent@test.com", hashed_password=pw, first_name="Dad", last_name="User", school_id=school.id)
    child = User(email="child@test.com", hashed_password=pw, first_name="Kid", last_name="User", school_id=school.id)
    db_session.add_all([parent, child])
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Login as parent
        login_res = await ac.post("/api/auth/login", data={"username": "parent@test.com", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Link child
        link_res = await ac.post(f"/api/relationships/link-child/{child.id}", headers=headers)
        assert link_res.status_code == 201

        # 3. List children
        list_res = await ac.get("/api/relationships/children", headers=headers)
        assert len(list_res.json()) == 1
        assert list_res.json()[0]["email"] == "child@test.com"

        # 4. Link again (idempotency)
        link_dup = await ac.post(f"/api/relationships/link-child/{child.id}", headers=headers)
        assert link_dup.status_code == 201
        assert link_dup.json()["message"] == "Already linked"

@pytest.mark.asyncio
async def test_link_child_from_other_school(db_session):
    # Setup two schools
    s1 = School(name="S1", slug="s1")
    s2 = School(name="S2", slug="s2")
    db_session.add_all([s1, s2])
    db_session.flush()

    pw = security.get_password_hash("password123")
    parent = User(email="p1@s1.com", hashed_password=pw, first_name="P1", last_name="U", school_id=s1.id)
    stranger = User(email="c2@s2.com", hashed_password=pw, first_name="C2", last_name="U", school_id=s2.id)
    db_session.add_all([parent, stranger])
    db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post("/api/auth/login", data={"username": "p1@s1.com", "password": "password123"})
        token = login_res.json()["access_token"]
        
        # Try to link child from other school
        response = await ac.post(f"/api/relationships/link-child/{stranger.id}", headers={"Authorization": f"Bearer {token}"})
        
    assert response.status_code == 404
    assert response.json()["detail"] == "Child not found in your school"
