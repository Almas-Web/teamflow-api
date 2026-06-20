from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, Field, EmailStr
from fastapi import HTTPException, status


class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=4)

    def __init__(self, **data):
        super().__init__(**data)
        if self.email:
            try:
                emailinfo = validate_email(self.email, check_deliverability=False)
                self.email = emailinfo.normalized
            except EmailNotValidError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not a valid email!"
                )


class UserView(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = {
        "from_attributes": True
    }
class Token(BaseModel):
   access_token: str
   refresh_token: str
   token_type: str = "bearer"
