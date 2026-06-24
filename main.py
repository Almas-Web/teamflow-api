from fastapi import FastAPI, Depends
from core.config import settings
from apis.base import api_router
from repositories.user import UserRepository
from db.models.user import User


def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,                       
        version=settings.PROJECT_VERSION
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