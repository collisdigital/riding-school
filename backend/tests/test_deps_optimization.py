import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import security
from app.main import app
from app.models.rbac import Role
from app.models.school import School
from app.models.user import User


@pytest.mark.asyncio
async def test_riders_list_works_with_optimization(db_session):
    # Setup
    email = f"opt_{uuid.uuid4()}@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)

    # Create school
    school = School(name=f"School {uuid.uuid4()}", slug=f"school-{uuid.uuid4()}")
    db_session.add(school)
    db_session.commit()

    # Ensure at least one role exists
    role = db_session.query(Role).first()
    if not role:
        role = Role(name="TestRoleOpt")
        db_session.add(role)
        db_session.commit()

    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Opt",
        last_name="User",
        school_id=school.id,
        roles=[role],
    )
    db_session.add(user)
    db_session.commit()

    # Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login", data={"username": email, "password": password}
        )
        assert login_res.status_code == 200, login_res.text
        token = login_res.json()["access_token"]

        # Access /api/riders/ (uses optimized fetch)
        response = await ac.get(
            "/api/riders/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        # If optimization failed, this would be 500.
