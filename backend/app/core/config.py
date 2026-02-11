from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Riding School Progress Tracker"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/riding_school"
    SECRET_KEY: str = "supersecretkey"  # In production, use a secure secret
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    model_config = ConfigDict(case_sensitive=True)


settings = Settings()
