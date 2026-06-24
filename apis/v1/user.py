from fastapi import APIRouter, HTTPException, Depends, status,Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from db.session import get_db
from repositories.user import UserRepository
from schemas.user import UserCreate, UserView, Token
from utils.jwt_manager import (
    create_access_token,
    create_refresh_token,
    verify_token
)

router = APIRouter()


# ---------------- REFRESH SCHEMA ----------------
class RefreshRequest(BaseModel):
    refresh_token: str


# ---------------- USER REPO ----------------
def get_user_repo(db: Session) -> UserRepository:
    return UserRepository(db)


# ---------------- REGISTER USER ----------------
@router.post("/", response_model=UserView, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    user_repo = get_user_repo(db)

    existing_user = user_repo.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return user_repo.create_user(
        name=payload.name,
        email=payload.email,
        password=payload.password
    )


# ---------------- LOGIN ----------------
@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)

    user = user_repo.get_user_for_token(
        email=form_data.username,
        password=form_data.password
    )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ---------------- REFRESH TOKEN ----------------
@router.post("/refresh", response_model=Token)
def refresh_access_token(
    refresh_token: str = Form(default=""),
    db: Session = Depends(get_db)
):
    token_data = verify_token(refresh_token)

    if not token_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    user_id = int(token_data.get("sub"))

    user = UserRepository(db).get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }