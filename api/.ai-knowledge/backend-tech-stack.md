# Backend Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.x (async)
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **DB:** PostgreSQL (Docker Compose locally)
- **LLM calls:** `anthropic` Python SDK, called from `services/order_parsing.py`
- **Testing:** pytest

## Commands

```
uvicorn app.main:app --reload      # run dev server
pytest                              # run tests
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Update this file when a new dependency is added.
