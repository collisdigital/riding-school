import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event

from app.core import security
from app.main import app
from app.models.rbac import Permission, Role, UserPermissionOverride
from app.models.school import School
from app.models.user import User


@pytest.fixture
def count_queries(db_session):
    class QueryCounter:
        def __init__(self):
            self.count = 0
            self.statements = []

        def __call__(self, conn, cursor, statement, parameters, context, executemany):
            self.count += 1
            self.statements.append(str(statement))

    counter = QueryCounter()
    event.listen(db_session.bind, "before_cursor_execute", counter)
    yield counter
    event.remove(db_session.bind, "before_cursor_execute", counter)


@pytest.mark.asyncio
async def test_get_me_query_optimization(db_session, count_queries):
    # Setup School
    school_slug = f"perf-school-{uuid.uuid4()}"
    school = School(name="Perf School", slug=school_slug)
    db_session.add(school)
    db_session.commit()

    # Create Role and Permission
    perm = Permission(name=f"test:perm:{uuid.uuid4()}", description="Test Permission")
    role = Role(name=f"TestRole:{uuid.uuid4()}", description="Test Role")
    role.permissions.append(perm)
    db_session.add_all([perm, role])
    db_session.commit()

    # Create User
    pw = security.get_password_hash("password123")
    email = f"user_perf_{uuid.uuid4()}@test.com"
    user = User(
        email=email,
        hashed_password=pw,
        first_name="User",
        last_name="Perf",
        school_id=school.id,
    )
    user.roles.append(role)

    # Add an override to ensure it would be loaded if we didn't optimize
    override = UserPermissionOverride(user=user, permission=perm, allow=True)
    db_session.add(user)
    db_session.add(override)
    db_session.commit()

    # Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": email, "password": "password123"},
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Reset query counter
        count_queries.count = 0
        count_queries.statements = []

        # Call get me
        res = await ac.get("/api/auth/me", headers=headers)
        assert res.status_code == 200

        # Check assertions
        assert count_queries.count == 1, f"Expected 1 query, got {count_queries.count}"

        found_override_join = any("user_permission_overrides" in stmt for stmt in count_queries.statements)
        assert not found_override_join, "Query should not join user_permission_overrides for get_me"
