import pytest
from fastapi.testclient import TestClient

from main import app
from db.session import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base_class import Base

# 🔥 TEST DATABASE (IMPORTANT)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create test DB
Base.metadata.create_all(bind=engine)


# override DB dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user(client):
    """create user for login test"""
    response = client.post("/users", json={
        "name": "Test User",
        "email": "test@gmail.com",
        "password": "123456"
    })
    return response.json()


@pytest.fixture
def token(client):
    """login and return token"""
    client.post("/users", json={
        "name": "Test User2",
        "email": "test2@gmail.com",
        "password": "123456"
    })

    response = client.post("/users/token", data={
        "username": "test2@gmail.com",
        "password": "123456"
    })

    return response.json()["access_token"]