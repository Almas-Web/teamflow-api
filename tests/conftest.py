import pytest
import pytest_asyncio
import redis.asyncio as redis
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


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_limiter():
    redis_connection = redis.from_url("redis://localhost:6380/0", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    yield
    await redis_connection.aclose()

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