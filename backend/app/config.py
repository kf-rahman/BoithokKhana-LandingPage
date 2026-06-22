"""Application settings, loaded from environment / backend/.env."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Async DB URL. SQLite locally; postgresql+asyncpg in production.
    database_url: str = "sqlite+aiosqlite:///./catering.db"

    # Claude order parsing.
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-4-8"

    # Admin dashboard shared PIN (an explicit, changeable decision — not
    # an assumed auth model). Override via ADMIN_PIN.
    admin_pin: str = "1234"

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
