from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import Optional

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from db.session import get_db
from db.models.user import User
from utils.password_manager import PasswordManager
from utils.jwt_manager import verify_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- GET USER BY EMAIL ----------------
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(
            func.lower(User.email) == func.lower(email)
        ).first()

    # ---------------- GET USER BY ID ----------------
    def get_user_by_id(self, id: int) -> Optional[User]:
        return self.db.query(User).filter(
            User.id == id,
            User.is_active == True
        ).first()

    # ---------------- CREATE USER ----------------
    def create_user(
        self,
        name: str,
        email: str,
        password: str,
        is_active: bool = True
    ) -> User:

        hashed_password = PasswordManager.get_password_hash(password)

        db_user = User(
            name=name,
            email=email,
            password=hashed_password,
            is_active=is_active
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)

        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        return db_user

    # ---------------- LOGIN CHECK ----------------
    def get_user_for_token(self, email: str, password: str) -> User:

        user = self.get_user_by_email(email)

        if not user or not PasswordManager.verify_password(password, user.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )

        return user

    # ---------------- CURRENT USER ----------------
    @staticmethod
    def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ) -> User:

        payload = verify_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user_id = payload.get("sub")

        user = db.query(User).filter(
            User.id == int(user_id)
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user