from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Riding School Progress Tracker"
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/riding_school"
    
    model_config = ConfigDict(case_sensitive=True)

settings = Settings()
