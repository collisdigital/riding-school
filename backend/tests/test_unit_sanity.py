import pytest
import uuid
from pydantic import ValidationError
from app.schemas import UserCreate, SchoolCreate, UserSchema
from app.schemas.rider import RiderCreate
from app.models.user import User
from app.api.deps import get_current_user
from unittest.mock import MagicMock
from jose import jwt
from app.core.config import settings

def test_pydantic_v2_config_style():
    """
    Ensure models are using Pydantic v2 ConfigDict and not the deprecated class Config.
    """
    # If it still used class Config, it wouldn't necessarily fail instantiation,
    # but we can check the class attributes.
    assert hasattr(UserSchema, "model_config")
    assert not hasattr(UserSchema, "Config")

def test_imports_sanity():
    """
    Import all API routers to catch NameErrors (missing imports) early.
    """
    from app.api import auth, schools, riders, relationships
    assert auth.router
    assert schools.router
    assert riders.router
    assert relationships.router

def test_lifespan_setup():
    """
    Verify the FastAPI app is using the lifespan context manager.
    """
    from app.main import app
    assert app.router.lifespan_context is not None

@pytest.mark.asyncio
async def test_get_current_user_uuid_conversion():
    """
    Test that get_current_user correctly converts string sub to UUID.
    This would have caught the AttributeError: 'str' object has no attribute 'hex'.
    """
    db = MagicMock()
    user_id = uuid.uuid4()
    
    # Create a mock token
    token = jwt.encode({"sub": str(user_id)}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Mock the query chain
    mock_query = db.query.return_value
    mock_options = mock_query.options.return_value
    mock_filter = mock_options.filter.return_value
    mock_filter.first.return_value = User(id=user_id, email="test@test.com")

    # This call should not raise AttributeError
    user = get_current_user(db=db, token=token)
    
    assert user.id == user_id
    # Verify the filter was called with a UUID object, not a string
    # The actual call is User.id == user_id (where user_id is a UUID)
    args, _ = mock_options.filter.call_args
    # The first argument is the binary expression. We check the value.
    expression = args[0]
    assert isinstance(expression.right.value, uuid.UUID)
