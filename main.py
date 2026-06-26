import os
import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from core.config import settings
from apis.base import api_router
from repositories.user import UserRepository
from db.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Redis connection
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6380/0")
    try:
        redis_connection = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_connection)
        print("--- Redis Connected & FastAPILimiter Initialized ---")
    except Exception as e:
        print(f"--- FAILED TO CONNECT TO REDIS: {e} ---")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return response

app.include_router(api_router)

@app.get("/")
def home():
    return {"msg": "Hello World"}

@app.get("/protected", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def protected_route(
    current_user: User = Depends(UserRepository.get_current_user)
):
    return {
        "message": f"Hello {current_user.email}, you are authorized!"
    }

@app.get("/test-limit", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
def test_limit():
    return {"msg": "This is rate limited"}