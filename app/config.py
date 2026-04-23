"""Файл с настройками и подключением базы данных и Celery"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #PostgreSQL
    POSTGRES_USER:str = Field(default="admin", description="Postgres User")
    POSTGRES_PASSWORD:str = Field(default="password", description="Postgres password")
    POSTGRES_DB:str = Field(default="postgres", description="Database name")
    POSTGRES_HOST:str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT:int = Field(default=5432, description="Postgres port")

    # Celery
    CELERY_BROKER_URL:str = Field(
        default="redis://localhost:6379/0",
        description="Celery Broker URL (Redis)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Формирует строку подключения к базе для asyncpg"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()