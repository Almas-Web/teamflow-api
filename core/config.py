from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

env_path = Path(".") / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "TeamFlow API"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "teamflow_db"

    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_ALGORITHM: str = "HS256"

    EMAIL_PROVIDER: str = "gmail"
    SENDER_EMAIL: str = ""
    EMAIL_PASSWORD: str = ""
    BREVO_API_KEY: str = ""
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_REGION: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Pydantic V2 
    model_config = ConfigDict(
        env_file=str(env_path),
        extra='forbid'
    )

settings = Settings()