"""
Test configuration and fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.core.database import Base, get_db
from backend.main import app


# Test database URL (using a test database)
TEST_DATABASE_URL = "postgresql://james@localhost/kpath_enterprise_test"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def setup_database(engine):
    """Create all tables for testing"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine, setup_database):
    """Create a new database session for each test"""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_service_data():
    """Sample service data for testing"""
    return {
        "name": "TestService",
        "description": "A test service for unit testing",
        "endpoint": "https://api.test.com/v1",
        "version": "1.0.0",
        "status": "active"
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "user",
        "attributes": {"department": "Testing"}
    }
