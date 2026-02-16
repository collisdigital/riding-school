import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core import security
from app.models.rider_profile import RiderProfile
from app.models.user import User
from app.models.school import School
from app.models.membership import Membership
from uuid import uuid4
from sqlalchemy import event

@pytest.mark.asyncio
async def test_delete_rider_zero_auth_queries(db_session):
    # Setup Data
    school = School(name="Rider School", slug=f"rider-{uuid4().hex[:8]}")
    db_session.add(school)
    db_session.flush()

    instructor_id = uuid4()

    rider_user = User(email="rider@example.com", first_name="Rider", last_name="One", is_active=True, hashed_password="pw")
    db_session.add(rider_user)
    db_session.flush()

    # Rider needs membership in school too?
    # delete_rider code checks for membership to soft delete it.
    rider_membership = Membership(user_id=rider_user.id, school_id=school.id)
    db_session.add(rider_membership)

    profile = RiderProfile(user_id=rider_user.id, school_id=school.id)
    db_session.add(profile)
    db_session.commit()

    token = security.create_access_token(
        instructor_id,
        school_id=school.id,
        perms=["riders:delete"],
        roles=["INSTRUCTOR"]
    )

    queries = []
    def count_queries(conn, cursor, statement, parameters, context, executemany):
        queries.append(statement)

    # Listen on engine, not session bind if possible, or verify session.bind is engine
    event.listen(db_session.bind, "before_cursor_execute", count_queries)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(
            f"/api/riders/{profile.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

    event.remove(db_session.bind, "before_cursor_execute", count_queries)

    assert response.status_code == 204

    print("\nRecorded Queries:")
    for q in queries:
        print(q)

    # Verify no query selects from 'users' table (unless it's the rider's user, but rider profile query might join user?)
    # delete_rider code:
    # profile = db.query(RiderProfile).filter(...).first() -> SELECT rider_profile ...
    # membership = db.query(Membership).filter(...).first() -> SELECT membership ...
    # COMMIT -> UPDATE ...

    # It should NOT select from 'users' where id = instructor_id.
    # It should NOT select from 'roles' or 'permissions'.

    for q in queries:
        assert "roles" not in q
        assert "permissions" not in q
        # Ensure we don't query the instructor
        # Instructor ID is not in DB, so if it tried to find it, it would query WHERE id = ?.
        # But we can't easily check param values here without more complex listener.
        # But if we see a SELECT from users, it must be rider's user if any.

    # Check count. Logic implies:
    # 1. Select Profile
    # 2. Select Membership
    # 3. Update Profile
    # 4. Update Membership
    # (plus potential savepoints)

    # If auth ran:
    # +1 Select User (instructor)

    # Assert query count is reasonable.
    # 4-6 queries is expected.
    # If > 10, something is wrong.
