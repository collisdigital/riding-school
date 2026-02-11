import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.models.school import School
from app.models.rbac import Role
from app.core import security

@pytest.fixture
def school_and_admin(db_session):
    # Setup school
    school = School(name="Test School", slug="test-school")
    db_session.add(school)
    db_session.flush()
    
    # Setup admin user
    email = "admin@test.com"
    password = "password123"
    admin_role = db_session.query(Role).filter(Role.name == "Admin").first()
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        first_name="Admin",
        last_name="Test",
        school_id=school.id,
        roles=[admin_role]
    )
    db_session.add(user)
    db_session.commit()
    
    return school, user, password

@pytest.mark.asyncio
async def test_rider_crud_and_isolation(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get token
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": admin.email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Rider
        create_res = await ac.post(
            "/api/riders/",
            json={"first_name": "Swift", "last_name": "Hoof"},
            headers=headers
        )
        assert create_res.status_code == 200
        rider_id = create_res.json()["id"]

        # 2. List Riders
        list_res = await ac.get("/api/riders/", headers=headers)
        assert len(list_res.json()) == 1
        assert list_res.json()[0]["first_name"] == "Swift"

        # 3. Get Single Rider
        get_res = await ac.get(f"/api/riders/{rider_id}", headers=headers)
        assert get_res.json()["first_name"] == "Swift"

        # 4. Isolation Test: Create another school and user
        other_school = School(name="Other", slug="other")
        db_session.add(other_school)
        db_session.flush()
        
        other_password = "password123"
        other_user = User(
            email="other@test.com",
            hashed_password=security.get_password_hash(other_password),
            first_name="Other",
            last_name="User",
            school_id=other_school.id
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Login as other user
        login_other = await ac.post("/api/auth/login", data={"username": "other@test.com", "password": other_password})
        other_token = login_other.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Verify other user CANNOT see the rider from the first school
        leak_res = await ac.get(f"/api/riders/{rider_id}", headers=other_headers)
        assert leak_res.status_code == 404 # Isolated
        
        list_leak = await ac.get("/api/riders/", headers=other_headers)
        assert len(list_leak.json()) == 0
