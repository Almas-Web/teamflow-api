from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from apis.base import api_router
from repositories.user import UserRepository
from db.models.user import User

# List of allowed origins, you can add specific domains or '*' for all origins
origins = [
   "http://localhost:3000",  # Frontend during development
   "https://your-frontend-domain.com",  # Production frontend
   "*",  # Allow all origins (use cautiously)
]

def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,                      
        version=settings.PROJECT_VERSION
    )
    
    # Adding CORSMiddleware to the FastAPI app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # List of allowed origins
        allow_credentials=True,  # Allow cookies and credentials to be sent
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
        allow_headers=["*"],  # Allowed headers
    )
    
    return app


app = start_application()

app.include_router(api_router)


@app.get("/")
def home():
    return {"msg": "Hello World"}


@app.get("/protected")
async def protected_route(
    current_user: User = Depends(UserRepository.get_current_user)
):
    return {
        "message": f"Hello {current_user.email}, you are authorized!"
    }