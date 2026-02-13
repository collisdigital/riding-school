import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event

from app.core import security
from app.main import app
from app.models.rbac import Permission, Relationship, Role
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
            self.statements.append(statement)

    counter = QueryCounter()
    event.listen(db_session.bind, "before_cursor_execute", counter)
    yield counter
    event.remove(db_session.bind, "before_cursor_execute", counter)


@pytest.mark.asyncio
async def test_get_children_n_plus_one(db_session, count_queries):
    # Setup School
    school_slug = f"perf-{uuid.uuid4()}"
    school = School(name="Performance School", slug=school_slug)
    db_session.add(school)
    db_session.commit()  # Commit to get ID

    # Create Parent
    pw = security.get_password_hash("password123")
    parent_email = f"parent_perf_{uuid.uuid4()}@test.com"
    parent = User(
        email=parent_email,
        hashed_password=pw,
        first_name="Parent",
        last_name="Perf",
        school_id=school.id,
    )
    db_session.add(parent)
    db_session.commit()

    # Create Role and Permission to trigger nested N+1 if any
    perm = Permission(name=f"test:perm:{uuid.uuid4()}", description="Test Permission")
    role = Role(name=f"TestRole:{uuid.uuid4()}", description="Test Role")
    role.permissions.append(perm)
    db_session.add_all([perm, role])
    db_session.commit()

    # Create 5 Children
    children = []
    for i in range(5):
        child = User(
            email=f"child_{i}_{uuid.uuid4()}@test.com",
            hashed_password=pw,
            first_name=f"Child{i}",
            last_name="Perf",
            school_id=school.id,
        )
        child.roles.append(role)
        children.append(child)

    db_session.add_all(children)
    db_session.commit()

    # Link Children
    relationships = []
    for child in children:
        relationships.append(Relationship(parent_id=parent.id, rider_id=child.id))
    db_session.add_all(relationships)
    db_session.commit()

    # Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": parent_email, "password": "password123"},
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Reset query counter
        count_queries.count = 0
        count_queries.statements = []

        # Call get children
        res = await ac.get("/api/relationships/children", headers=headers)
        assert res.status_code == 200
        assert len(res.json()) == 5

        # Check query count
        # Expectation with optimization:
        # 1. Login/deps query
        # 2. Main query (relationships + rider)
        # 3. Roles query (selectinload)
        # 4. Permissions query (selectinload)
        # Total should be <= 5 queries. Without optimization it was 13.
        assert (
            count_queries.count <= 5
        ), f"Query count is {count_queries.count}, expected <= 5"
