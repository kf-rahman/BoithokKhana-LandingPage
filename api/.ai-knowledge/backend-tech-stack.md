# Backend Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.x (async, `aiosqlite` / `asyncpg`)
- **Migrations:** Alembic (sync driver — `sqlite` / `psycopg` — derived from
  the async `DATABASE_URL` in `alembic/env.py`)
- **Validation:** Pydantic v2 (`pydantic-settings` for config)
- **DB:** defaults to SQLite (`sqlite+aiosqlite`) so local dev needs no
  Docker; `postgresql+asyncpg` in production / via Docker Compose.
- **LLM calls:** `anthropic` Python SDK, called from
  `services/order_parsing.py`. The synchronous SDK call is isolated in
  `_request_structured_parse` and run via `asyncio.to_thread` (mockable in
  tests, off the event loop).
- **Testing:** pytest + `pytest-asyncio` (async client over httpx
  ASGITransport, in-memory SQLite via StaticPool)

## Commands

```
uvicorn app.main:app --reload      # run dev server
pytest                              # run tests
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Update this file when a new dependency is added.
