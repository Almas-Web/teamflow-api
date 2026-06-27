from pathlib import Path
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings
import os

env_path = Path(".") / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "TeamFlow API"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5435"
    POSTGRES_DB: str = "teamflow_db"

    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"
    EMAIL_PROVIDER: str = "gmail"
    SENDER_EMAIL: str = ""
    EMAIL_PASSWORD: str = ""

    # 

    @property
    def DATABASE_URL(self) -> str:
        
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
        
        
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = ConfigDict(
        env_file=".env",
        extra='ignore' 
    )

settings = Settings()