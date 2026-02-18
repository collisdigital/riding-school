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
    # Setup school
    uid = uuid.uuid4().hex[:8]
    school = School(name=f"School {uid}", slug=f"school-{uid}")
    db_session.add(school)
    db_session.flush()

    # Setup admin
    password = "password123"
    user = User(
        email=f"admin_{uid}@test.com",
        hashed_password=security.get_password_hash(password),
        first_name="Admin",
        last_name="Test",
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    # Ensure Admin Role exists
    admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    if not admin_role:
        # Should be seeded by conftest, but just in case
        admin_role = Role(name=Role.ADMIN, description="Administrator")
        db_session.add(admin_role)
        db_session.flush()

    mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
    db_session.add(mem_role)
    db_session.commit()

    return school, user, password


@pytest.mark.asyncio
async def test_grades_crud(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Login
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Grade
        res = await ac.post(
            "/api/grades/",
            json={"name": "Grade 1", "description": "Beginner"},
            headers=headers,
        )
        assert res.status_code == 200
        grade1 = res.json()
        assert grade1["name"] == "Grade 1"
        assert grade1["sequence_order"] == 0

        # 2. Create another Grade
        res = await ac.post("/api/grades/", json={"name": "Grade 2"}, headers=headers)
        grade2 = res.json()
        assert grade2["sequence_order"] == 1

        # 3. Add Skill
        res = await ac.post(
            f"/api/grades/{grade1['id']}/skills", json={"name": "Walk"}, headers=headers
        )
        assert res.status_code == 200
        skill = res.json()
        assert skill["name"] == "Walk"
        assert skill["grade_id"] == grade1["id"]

        # 4. List Grades
        res = await ac.get("/api/grades/", headers=headers)
        grades = res.json()
        assert len(grades) == 2
        assert grades[0]["id"] == grade1["id"]
        assert len(grades[0]["skills"]) == 1

        # 5. Reorder
        # Swap: [Grade 2, Grade 1]
        res = await ac.patch(
            "/api/grades/reorder",
            json={"ordered_ids": [grade2["id"], grade1["id"]]},
            headers=headers,
        )
        assert res.status_code == 204

        # Verify order
        res = await ac.get("/api/grades/", headers=headers)
        grades = res.json()
        assert grades[0]["id"] == grade2["id"]
        assert grades[0]["sequence_order"] == 0
        assert grades[1]["id"] == grade1["id"]
        assert grades[1]["sequence_order"] == 1

        # 6. Delete
        res = await ac.delete(f"/api/grades/{grade2['id']}", headers=headers)
        assert res.status_code == 204

        res = await ac.get("/api/grades/", headers=headers)
        grades = res.json()
        assert len(grades) == 1
        assert grades[0]["id"] == grade1["id"]


@pytest.mark.asyncio
async def test_rider_grade_assignment(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Grade
        g_res = await ac.post("/api/grades/", json={"name": "G1"}, headers=headers)
        grade_id = g_res.json()["id"]

        # Create Rider
        r_res = await ac.post(
            "/api/riders/",
            json={"first_name": "Rider", "last_name": "One"},
            headers=headers,
        )
        rider_id = r_res.json()["id"]

        # Assign Grade
        res = await ac.patch(
            f"/api/riders/{rider_id}/grade",
            json={"grade_id": grade_id},
            headers=headers,
        )
        assert res.status_code == 204

        # Move to same grade (idempotent/no-op)
        res = await ac.patch(
            f"/api/riders/{rider_id}/grade",
            json={"grade_id": grade_id},
            headers=headers,
        )
        assert res.status_code == 204

        # Create Grade 2
        g2_res = await ac.post("/api/grades/", json={"name": "G2"}, headers=headers)
        grade2_id = g2_res.json()["id"]

        # Move to Grade 2
        res = await ac.patch(
            f"/api/riders/{rider_id}/grade",
            json={"grade_id": grade2_id},
            headers=headers,
        )
        assert res.status_code == 204


@pytest.mark.asyncio
async def test_skill_crud(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create Grade
        g_res = await ac.post("/api/grades/", json={"name": "G1"}, headers=headers)
        grade_id = g_res.json()["id"]

        # Create Skill
        s_res = await ac.post(
            f"/api/grades/{grade_id}/skills", json={"name": "Jump"}, headers=headers
        )
        assert s_res.status_code == 200
        skill_id = s_res.json()["id"]

        # Update Skill
        u_res = await ac.put(
            f"/api/grades/skills/{skill_id}",
            json={"name": "Jump High", "description": "Over 1m"},
            headers=headers,
        )
        assert u_res.status_code == 200
        assert u_res.json()["name"] == "Jump High"
        assert u_res.json()["description"] == "Over 1m"

        # Delete Skill
        d_res = await ac.delete(f"/api/grades/skills/{skill_id}", headers=headers)
        assert d_res.status_code == 204

        # Verify Deleted
        list_res = await ac.get("/api/grades/", headers=headers)
        grade = list_res.json()[0]
        assert len(grade["skills"]) == 0


@pytest.mark.asyncio
async def test_delete_grade_protection(db_session, school_and_admin):
    school, admin, password = school_and_admin
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": admin.email, "password": password}
        )
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        # Create Grade & Rider
        g_res = await ac.post("/api/grades/", json={"name": "G1"}, headers=headers)
        grade_id = g_res.json()["id"]
        r_res = await ac.post(
            "/api/riders/",
            json={"first_name": "R1", "last_name": "L1"},
            headers=headers,
        )
        rider_id = r_res.json()["id"]

        # Assign Grade
        await ac.patch(
            f"/api/riders/{rider_id}/grade",
            json={"grade_id": grade_id},
            headers=headers,
        )

        # Attempt Delete
        del_res = await ac.delete(f"/api/grades/{grade_id}", headers=headers)
        assert del_res.status_code == 409
        assert "referenced by rider history" in del_res.json()["detail"]
