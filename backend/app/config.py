"""Application settings, overridable via environment variables or a .env file."""

from pydantic import field_validator
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

    # Error reporting (Sentry). Blank DSN = disabled, which is the default:
    # nothing is sent anywhere until SENTRY_DSN is set. See app/observability.py.
    sentry_dsn: str = ""
    # Tags events so staging noise never gets mistaken for a real customer
    # problem in production.
    sentry_environment: str = "development"
    # Fraction of requests traced for performance (0.0 = errors only). Kept at
    # zero so the free tier's quota is spent on errors, not traces.
    sentry_traces_sample_rate: float = 0.0

    @field_validator("database_url")
    @classmethod
    def _normalise_database_url(cls, value: str) -> str:
        """Accept the `postgres://` URLs that hosting providers hand out.

        Render (and Heroku, and several others) inject DATABASE_URL in the form
        `postgres://user:pass@host/db`. SQLAlchemy 2.x does not recognise that
        scheme and fails at import time with:

            Can't load plugin: sqlalchemy.dialects:postgres

        Rewriting it here means the app boots from a provider-supplied URL
        unchanged, and both the engine and Alembic (which read this same
        setting) stay consistent.
        """
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://") :]
        # `postgresql://` alone would pick SQLAlchemy's default driver
        # (psycopg2), which isn't installed — psycopg 3 is. Be explicit.
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://") :]
        return value


settings = Settings()
