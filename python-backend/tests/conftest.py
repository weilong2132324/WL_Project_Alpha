"""Test configuration and fixtures"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.config import AppConfig, ServerConfig, DBConfig, RedisConfig, set_config


# Create test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    """Setup test configuration"""
    test_config = AppConfig(
        server=ServerConfig(
            env="test",
            address="127.0.0.1",
            port=8000,
            jwt_secret="test-secret",
            db_type="sqlite"
        ),
        sqlite=DBConfig(file="./test.db"),
        redis=RedisConfig(enable=False)
    )
    set_config(test_config)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client"""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Create a test user"""
    from app.models import User
    from app.utils.auth import hash_password
    
    user = User(
        name="testuser",
        email="test@example.com",
        password=hash_password("testpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user"""
    from app.utils.auth import create_access_token
    
    token = create_access_token(test_user.id, test_user.name)
    return {"Authorization": f"Bearer {token}"}
