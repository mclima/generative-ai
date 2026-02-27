import os
import pytest

# Set test environment variables before importing app modules
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test_db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["TESTING"] = "true"  # Disable CSRF protection in tests

from sqlalchemy import create_engine, event, TypeDecorator, CHAR, Text, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
import fakeredis
import uuid as uuid_pkg
import json

from app.database import Base
from app.config import get_settings


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid_pkg.UUID):
                return str(value)
            else:
                return str(uuid_pkg.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid_pkg.UUID):
                return value
            else:
                return uuid_pkg.UUID(value)


class JSONType(TypeDecorator):
    """Platform-independent JSON type.
    Uses PostgreSQL's JSONB type, otherwise uses Text, storing as JSON strings.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return json.loads(value)


class INETType(TypeDecorator):
    """Platform-independent INET type.
    Uses PostgreSQL's INET type, otherwise uses String, storing as IP address strings.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(INET())
        else:
            return dialect.type_descriptor(String(45))  # Max length for IPv6

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        return value


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Replace UUID, JSONB, and INET columns for SQLite compatibility
    @event.listens_for(Base.metadata, "before_create")
    def receive_before_create(target, connection, **kw):
        """Replace PostgreSQL-specific types with compatible types for SQLite."""
        for table in target.tables.values():
            for column in table.columns:
                if isinstance(column.type, UUID):
                    column.type = GUID()
                elif isinstance(column.type, JSONB):
                    column.type = JSONType()
                elif isinstance(column.type, INET):
                    column.type = INETType()
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def redis_client():
    """Create a fake Redis client for testing."""
    fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)
    yield fake_redis
    fake_redis.flushall()


@pytest.fixture(scope="function")
def settings():
    """Get settings for testing."""
    return get_settings()


# Imports for API testing
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.redis_client import get_redis
from app.models import User
from app.services.auth_service import AuthService
import bcrypt


@pytest.fixture(scope="function")
def test_db(db_session):
    """Override the get_db dependency to use test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield db_session
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_redis(redis_client):
    """Override the get_redis dependency to use fake Redis."""
    def override_get_redis():
        return redis_client
    
    app.dependency_overrides[get_redis] = override_get_redis
    yield redis_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db, test_redis):
    """Create a test client with overridden dependencies."""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user(test_db):
    """Create a test user in the database."""
    password = "testpassword123"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        email="test@example.com",
        password_hash=password_hash
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Store the plain password for testing
    user.plain_password = password
    
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user, test_db, test_redis):
    """Create authentication headers for test requests."""
    auth_service = AuthService(test_db, test_redis)
    
    # Login to get tokens
    result = auth_service.login(test_user.email, test_user.plain_password)
    
    return {
        "Authorization": f"Bearer {result['access_token']}"
    }
