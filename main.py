import os
import time
import redis.asyncio as redis
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from loguru import logger

from core.config import settings
from apis.base import api_router
from repositories.user import UserRepository
from db.models.user import User
from core.exceptions import global_exception_handler
from fastapi import HTTPException

# logs folder creation
if not os.path.exists("logs"):
    os.makedirs("logs")
logger.add("logs/app.log", rotation="10 MB", level="INFO")

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
#exception handler
@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    return await global_exception_handler(request, exc)

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

# logging middleware to log incoming requests and their responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Incoming Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Time: {process_time:.4f}s")
    
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

