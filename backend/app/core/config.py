from pydantic import ConfigDict, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Riding School Progress Tracker"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/riding_school"
    SECRET_KEY: str = "supersecretkey"  # Override in non-dev environments
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "development"
    SECURE_COOKIES: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    model_config = ConfigDict(case_sensitive=True)

    @model_validator(mode="after")
    def validate_secret_key(self):
        if self.ENVIRONMENT != "development" and (
            not self.SECRET_KEY or self.SECRET_KEY == "supersecretkey"
        ):
            raise ValueError("SECRET_KEY must be set to a secure value")
        return self


settings = Settings()
