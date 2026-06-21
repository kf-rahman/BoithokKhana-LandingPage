"""Application settings, overridable via environment variables or a .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Family Catering Order System API"

    # Origins allowed to call the API from the browser (the Next.js dev server).
    cors_origins: list[str] = ["http://localhost:3000"]

    # Local dev uses SQLite (no Docker yet). Swap to Postgres later by setting
    # DATABASE_URL — the models/migrations are kept portable.
    database_url: str = "sqlite:///./boithok.db"

    # Shared admin PIN protecting the menu/admin endpoints (README's v1 auth).
    # Override via ADMIN_PIN — CHANGE this before any real deployment.
    admin_pin: str = "1234"

    # Claude API (order parsing). Parsing is disabled until a key is set.
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-8"

    # Email (customer order confirmations). Disabled until SMTP_HOST is set;
    # set the SMTP_* vars to a real provider (SES, SendGrid, etc.) for production.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "orders@boithokkhana.ca"
    smtp_use_tls: bool = True


settings = Settings()
