import os
os.environ["TESTING"] = "True"

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from fastapi_limiter import FastAPILimiter
from main import app
from db.session import get_db
from db.base_class import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DB Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def dummy_identifier(request):
    return "test"

async def dummy_callback(request, response, pexpire):
    
    return None

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_limiter():
    
    mock_redis = AsyncMock()
 
    mock_redis.execute_command = AsyncMock(return_value=0)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)

    await FastAPILimiter.init(
        mock_redis, 
        identifier=dummy_identifier, 
        http_callback=dummy_callback
    )
    
    yield
 
    FastAPILimiter.redis = None
    FastAPILimiter.identifier = None
    FastAPILimiter.http_callback = None

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac