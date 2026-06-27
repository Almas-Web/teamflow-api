import os
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from fastapi_limiter import FastAPILimiter
from fastapi import Request, Response
from main import app
from db.session import get_db
from db.base_class import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DB Setup for Testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async Identifier and Callback for Limiter
async def dummy_identifier(request: Request):
    return "test"

async def dummy_callback(request: Request, response: Response, pexpire: int):
    return None

# Limiter Fixture
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_limiter():
    mock_redis = AsyncMock()
    
    await FastAPILimiter.init(
        mock_redis, 
        identifier=dummy_identifier, 
        http_callback=dummy_callback
    )
    
    yield
    
   
    FastAPILimiter.redis = None

# DB Setup Fixture
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Dependency Override
@pytest.fixture(scope="function", autouse=True)
def override_db_dependency():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear() 

# Async Client Fixture
@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac