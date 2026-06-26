import sys
import os
import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi.testclient import TestClient
from fastapi_limiter import FastAPILimiter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# App import
from main import app
from db.session import get_db
from db.base_class import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fixture for Redis Rate Limiter
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_limiter():
    redis_connection = redis.from_url("redis://localhost:6380/0", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield
    #await redis_connection.close()
    await redis_connection.aclose()

# Fixture to clear and recreate DB before every test
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)  # Delete old data
    Base.metadata.create_all(bind=engine)  # Recreate tables
    yield
    Base.metadata.drop_all(bind=engine)  # Clean up after test

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)

# NEW FIXTURE: Create a workspace automatically for tests
@pytest.fixture
def workspace(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/workspaces", json={"name": "Test Workspace"}, headers=headers)
    return response.json()

# UPDATE: Use 'workspace' fixture to get the correct ID
@pytest.fixture
def authorized_client(client, token):
    client.headers = {"Authorization": f"Bearer {token}"}
    return client