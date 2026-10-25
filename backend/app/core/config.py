from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "DukanIQ"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dukaniq.db"
    SECRET_KEY: str = "dukaniq-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
