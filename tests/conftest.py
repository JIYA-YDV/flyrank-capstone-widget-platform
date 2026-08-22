# tests/conftest.py
import os
import sys
import pytest
from unittest.mock import patch

# Ensure app is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Use SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-tests"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.db.session import Base, get_db
from app.main import app
from app.middleware.rate_limiter import limiter

# In-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset slowapi rate limits before every test."""
    try:
        limiter.reset()
    except Exception:
        pass


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "company_name": "Test Corp",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_widget(client, auth_headers):
    """Create and return a sample widget."""
    response = client.post(
        "/api/widgets",
        json={
            "name": "Test Contact Form",
            "widget_type": "contact_form",
            "title": "Contact Us",
            "description": "Test form",
            "fields_config": [
                {"name": "name", "label": "Name", "field_type": "text", "required": True},
                {"name": "email", "label": "Email", "field_type": "email", "required": True},
                {"name": "message", "label": "Message", "field_type": "textarea", "required": False},
            ],
            "button_text": "Submit",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()