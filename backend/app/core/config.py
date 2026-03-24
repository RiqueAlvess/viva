from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import secrets


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def ensure_async_driver(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql+psycopg2://"):
            v = v.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        return v

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Resend
    RESEND_API_KEY: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Encryption
    ENCRYPTION_KEY: str

    # Environment
    ENVIRONMENT: str = "development"

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker(cls, v, info):
        if v is None:
            return info.data.get("REDIS_URL", "redis://localhost:6379/0")
        return v

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_backend(cls, v, info):
        if v is None:
            return info.data.get("REDIS_URL", "redis://localhost:6379/0")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
