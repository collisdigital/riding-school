import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.auth import login_limiter
from app.core.seed import seed_rbac
from app.db import Base, get_db
from app.main import app

# Use an in-memory SQLite for tests or a test postgres
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_rbac(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clear_rate_limit():
    login_limiter.requests.clear()
    yield
    login_limiter.requests.clear()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
