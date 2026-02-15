import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.school import School
from app.models.user import User


@pytest.fixture
def school_and_admin(db_session):
    # Setup school with unique name
    uid = uuid.uuid4().hex[:8]
    school_name = f"Test School {uid}"
    school_slug = f"test-school-{uid}"

    school = School(name=school_name, slug=school_slug)
    db_session.add(school)
    db_session.flush()

    # Setup admin user
    email = f"admin_{uid}@test.com"
    password = "password123"

    # Create User
    user = User(
        email=email,
        hashed_password=security.get_password_hash(password),
        first_name="Admin",
        last_name="Test",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    # Create Membership
    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    # Assign Admin Role
    admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
    db_session.add(mem_role)

    db_session.commit()

    return school, user, password


@pytest.mark.asyncio
async def test_rider_crud_and_isolation(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get token
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Rider (New User)
        create_res = await ac.post(
            "/api/riders/",
            json={
                "first_name": "Swift",
                "last_name": "Hoof",
                "email": f"swift_{school.slug}@hoof.com",
                "height_cm": 170.5,
                "weight_kg": 60.0,
                "date_of_birth": "2010-01-01",
            },
            headers=headers,
        )
        assert create_res.status_code == 200, create_res.text
        data = create_res.json()
        rider_id = data["id"]
        assert data["first_name"] == "Swift"
        assert data["height_cm"] == 170.5

        # 2. List Riders
        list_res = await ac.get("/api/riders/", headers=headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        # Filter to find ours (since DB might have others from other tests)
        found = [r for r in list_res.json() if r["id"] == rider_id]
        assert len(found) == 1

        # 3. Get Single Rider
        get_res = await ac.get(f"/api/riders/{rider_id}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["first_name"] == "Swift"

        # 4. Update Rider
        update_res = await ac.put(
            f"/api/riders/{rider_id}",
            json={"first_name": "Swifter", "height_cm": 175.0},
            headers=headers,
        )
        assert update_res.status_code == 200
        assert update_res.json()["first_name"] == "Swifter"
        assert update_res.json()["height_cm"] == 175.0

        # 5. Isolation Test: Create another school and user
        uid2 = uuid.uuid4().hex[:8]
        other_school = School(name=f"Other {uid2}", slug=f"other-{uid2}")
        db_session.add(other_school)
        db_session.flush()

        other_password = "password123"
        other_user = User(
            email=f"other_{uid2}@test.com",
            hashed_password=security.get_password_hash(other_password),
            first_name="Other",
            last_name="User",
            is_active=True,
        )
        db_session.add(other_user)
        db_session.flush()

        other_mem = Membership(user_id=other_user.id, school_id=other_school.id)
        db_session.add(other_mem)
        db_session.flush()

        # Assign Admin Role to other user
        admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
        mem_role_other = MembershipRole(
            membership_id=other_mem.id,
            role_id=admin_role.id,
        )
        db_session.add(mem_role_other)

        db_session.commit()

        # Login as other user
        login_other = await ac.post(
            "/api/auth/login",
            data={"username": other_user.email, "password": other_password},
        )
        other_token = login_other.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        # Verify other user CANNOT see the rider from the first school
        leak_res = await ac.get(f"/api/riders/{rider_id}", headers=other_headers)
        assert leak_res.status_code == 404  # Isolated

        list_leak = await ac.get("/api/riders/", headers=other_headers)
        # Should be 0 in OTHER school
        assert len(list_leak.json()) == 0

        # 6. Delete Rider (back as admin)
        delete_res = await ac.delete(f"/api/riders/{rider_id}", headers=headers)
        assert delete_res.status_code == 204

        # Verify deletion (soft delete check handled by automatic filter)
        get_deleted = await ac.get(f"/api/riders/{rider_id}", headers=headers)
        assert get_deleted.status_code == 404

        list_deleted = await ac.get("/api/riders/", headers=headers)
        found_deleted = [r for r in list_deleted.json() if r["id"] == rider_id]
        assert len(found_deleted) == 0


@pytest.mark.asyncio
async def test_rider_create_no_email_managed_user(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create rider with NO email
        res = await ac.post(
            "/api/riders/",
            json={
                "first_name": "Kid",
                "last_name": "NoEmail",
                # email omitted
                "height_cm": 120.0,
            },
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        assert data["email"] is None
        assert data["first_name"] == "Kid"

        # Check DB
        # We can query API
        get_res = await ac.get(f"/api/riders/{data['id']}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.json()["email"] is None


@pytest.mark.asyncio
async def test_rider_create_existing_user_link(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    # Create a pre-existing user (global)
    uid = uuid.uuid4().hex[:8]
    email = f"existing_{uid}@user.com"
    pre_user = User(
        email=email,
        first_name="Existing",
        last_name="User",
        is_active=True,
        hashed_password=security.get_password_hash("pass"),
    )
    db_session.add(pre_user)
    db_session.commit()

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create rider with existing email
        res = await ac.post(
            "/api/riders/",
            json={
                "first_name": "Existing",
                "last_name": "User",
                "email": email,
                "height_cm": 180.0,
            },
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()

        # Should link to same user ID
        assert data["user_id"] == str(pre_user.id)
        assert data["email"] == email
