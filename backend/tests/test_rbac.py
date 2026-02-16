import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app
from app.models.membership import Membership, MembershipRole
from app.models.role import Role
from app.models.school import School
from app.models.user import User


@pytest.mark.asyncio
async def test_instructor_cannot_delete_rider(db_session):
    # RBAC seeding is handled by setup_test_db fixture in conftest.py

    # 1. Setup: Create School
    school = School(name="Test School", slug=f"test-school-{uuid.uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    # 2. Setup: Create an Instructor user
    email = "instructor@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Instructor",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    instructor_role = (
        db_session.query(Role).filter(Role.name == Role.INSTRUCTOR).first()
    )
    # Ensure role exists (handled by seed_rbac but safe check)
    assert instructor_role, "Instructor role should exist"

    mem_role = MembershipRole(membership_id=membership.id, role_id=instructor_role.id)
    db_session.add(mem_role)

    db_session.commit()

    # 3. Login to get token
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 4. Try to delete a (non-existent) rider to check permission
        # Even if the rider doesn't exist, the permission check happens first.
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403
    # The message is now from RequirePermission dependency
    assert "Missing required permission: riders:delete" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_can_delete_rider(db_session):
    # RBAC seeding is handled by setup_test_db fixture in conftest.py

    # 1. Setup: Create School
    school = School(name="Admin School", slug=f"admin-school-{uuid.uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    # 2. Setup: Create an Admin user
    email = "admin@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    assert admin_role, "Admin role should exist"

    mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
    db_session.add(mem_role)

    db_session.commit()

    # 3. Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 4. Try to delete - should get 404 (not found) instead of 403 (forbidden)
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}", headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 404  # Permission passed, but rider not found


@pytest.mark.asyncio
async def test_school_isolation(db_session):
    """
    Test that a user with 'riders:delete' (via Admin role) in School A
    does NOT have it in School B (where they are Instructor).
    """
    # RBAC seeding is handled by setup_test_db fixture in conftest.py

    # 1. Setup: Two Schools
    school_a = School(name="School A", slug=f"school-a-{uuid.uuid4().hex[:8]}")
    school_b = School(name="School B", slug=f"school-b-{uuid.uuid4().hex[:8]}")
    db_session.add(school_a)
    db_session.add(school_b)
    db_session.flush()

    # 2. Setup: User
    email = "isolation@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Iso",
        last_name="User",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    # 3. Roles
    admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    instructor_role = (
        db_session.query(Role).filter(Role.name == Role.INSTRUCTOR).first()
    )

    assert admin_role, "Admin role should exist"
    assert instructor_role, "Instructor role should exist"

    # 4. Membership: Admin in School A
    mem_a = Membership(user_id=user.id, school_id=school_a.id)
    db_session.add(mem_a)
    db_session.flush()
    db_session.add(MembershipRole(membership_id=mem_a.id, role_id=admin_role.id))

    # 5. Membership: Instructor in School B
    mem_b = Membership(user_id=user.id, school_id=school_b.id)
    db_session.add(mem_b)
    db_session.flush()
    db_session.add(MembershipRole(membership_id=mem_b.id, role_id=instructor_role.id))

    db_session.commit()

    # 6. Test Access in School B (Instructor -> Cannot delete)
    # Generate token manually for School B context with correct perms
    # mem_b (Instructor) has NO "riders:delete"
    # Instructor perms: riders:view, grades:signoff, grades:view_history
    token_b = security.create_access_token(
        user.id,
        school_id=school_b.id,
        perms=mem_b.permissions,
        roles=[r.name for r in [instructor_role]],
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}", headers={"Authorization": f"Bearer {token_b}"}
        )

    assert response.status_code == 403, "Should be forbidden in School B (Instructor)"
    assert "Missing required permission: riders:delete" in response.json()["detail"]

    # 7. Test Access in School A (Admin -> Can delete)
    # mem_a (Admin) HAS "riders:delete" (via "all")
    token_a = security.create_access_token(
        user.id,
        school_id=school_a.id,
        perms=mem_a.permissions,
        roles=[r.name for r in [admin_role]],
    )

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}", headers={"Authorization": f"Bearer {token_a}"}
        )

    assert (
        response.status_code == 404
    ), "Should be allowed (not found) in School A (Admin)"


@pytest.mark.asyncio
async def test_admin_can_update_rider(db_session):
    # RBAC seeding is handled by setup_test_db fixture in conftest.py

    # 1. Setup: Create School
    school = School(name="Update School", slug=f"update-school-{uuid.uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    # 2. Setup: Create an Admin user
    email = "updater@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Updater",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    membership = Membership(user_id=user.id, school_id=school.id)
    db_session.add(membership)
    db_session.flush()

    admin_role = db_session.query(Role).filter(Role.name == Role.ADMIN).first()
    assert admin_role, "Admin role should exist"

    # Verify Admin has permission (seed_rbac should have done this)
    # This assertion helps verify the test setup itself
    has_perm = any(p.name == "riders:update" for p in admin_role.permissions)
    assert has_perm, "Admin role must have riders:update permission"

    mem_role = MembershipRole(membership_id=membership.id, role_id=admin_role.id)
    db_session.add(mem_role)

    db_session.commit()

    # 3. Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]

        # 4. Try to update - should get 404 (not found) instead of 403 (forbidden)
        # This confirms that the user has "riders:update" permission
        fake_id = str(uuid.uuid4())
        response = await ac.put(
            f"/api/riders/{fake_id}",
            json={"first_name": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404
