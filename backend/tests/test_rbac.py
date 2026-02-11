import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.models.user import User
from app.models.rbac import Role, Permission
from app.core import security

@pytest.mark.asyncio
async def test_instructor_cannot_delete_rider(db_session):
    # 1. Setup: Create an Instructor user
    email = "instructor@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)
    
    instructor_role = db_session.query(Role).filter(Role.name == "Instructor").first()
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Instructor",
        roles=[instructor_role]
    )
    db_session.add(user)
    db_session.commit()
    
    # 2. Login to get token
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]
        
        # 3. Try to delete a (non-existent) rider to check permission
        # Even if the rider doesn't exist, the permission check happens first.
        import uuid
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
    assert response.status_code == 403
    assert "Missing required permission: riders:delete" in response.json()["detail"]

@pytest.mark.asyncio
async def test_admin_can_delete_rider(db_session):
    # 1. Setup: Create an Admin user
    email = "admin@example.com"
    password = "password123"
    hashed_password = security.get_password_hash(password)
    
    admin_role = db_session.query(Role).filter(Role.name == "Admin").first()
    
    user = User(
        email=email,
        hashed_password=hashed_password,
        first_name="Mark",
        last_name="Admin",
        roles=[admin_role]
    )
    db_session.add(user)
    db_session.commit()
    
    # 2. Login
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        login_res = await ac.post(
            "/api/auth/login",
            data={"username": email, "password": password}
        )
        token = login_res.json()["access_token"]
        
        # 3. Try to delete - should get 404 (not found) instead of 403 (forbidden)
        import uuid
        fake_id = str(uuid.uuid4())
        response = await ac.delete(
            f"/api/riders/{fake_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
    assert response.status_code == 404 # Permission passed, but rider not found
