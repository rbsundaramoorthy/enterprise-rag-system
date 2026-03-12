from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ENTERPRISE_RAG_",
        extra="ignore",
    )

    app_name: str = "enterprise-rag-api"
    environment: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    postgres_dsn: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/enterprise_rag"
    )
    redis_dsn: str = Field(default="redis://localhost:6379/0")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

