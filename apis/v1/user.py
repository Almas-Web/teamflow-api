from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from db.session import get_db
from repositories.user import UserRepository
from schemas.user import UserCreate, UserView
from schemas.user import Token
from utils.jwt_manager import create_access_token, create_refresh_token, verify_token

router = APIRouter()


def get_user_repo(db: Session) -> UserRepository:
    return UserRepository(db)


@router.post("", response_model=UserView)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db)
):
    user_repo = get_user_repo(db=db)

    existing_user = user_repo.get_user_by_email(email=payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = user_repo.create_user(
        name=payload.name,
        email=payload.email,
        password=payload.password
    )

    return new_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = UserRepository(db=db).get_user_for_token(
        email=form_data.username,
        password=form_data.password
    )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    payload = verify_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    payload_subject = payload.get("sub")

    user = UserRepository(db=db).get_user_by_id(id=payload_subject)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }