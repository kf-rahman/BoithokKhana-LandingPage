# Backend — Family Catering Order System (FastAPI)

## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```
uvicorn app.main:app --reload     # http://localhost:8000
```

- Health check: `GET http://localhost:8000/health`
- Interactive docs: http://localhost:8000/docs

## Test

```
python -m pytest
```

> The pre-commit hook runs `python -m pytest` whenever `backend/` files are
> staged, using whatever Python is active in your shell. **Activate `.venv`
> before committing** (or install the deps into your active environment) or the
> hook will block the commit.

> PostgreSQL (SQLAlchemy + Alembic) is not wired yet — it's added in a later task.
