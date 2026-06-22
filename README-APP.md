# Boithok Khana — Order System (Workflow 3 build)

Free-text catering orders parsed by Claude into structured line items,
managed from a PIN-protected admin dashboard. This branch (`workflow3`) is
the Deschryver-workflow build — see `AGENTS.md` and `specs/`.

## Run locally (no Docker)

The backend defaults to SQLite, so nothing else is needed.

```bash
# backend  →  http://localhost:8000
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env          # add ANTHROPIC_API_KEY, set ADMIN_PIN
.venv/bin/python seed.py      # seed a sample menu
.venv/bin/uvicorn app.main:app --reload

# frontend →  http://localhost:3000
cd frontend
npm install
npm run dev
```

Tables auto-create on first start. To use Alembic instead:
`cd backend && .venv/bin/alembic upgrade head`.

## Run with Postgres (Docker Compose)

```bash
ANTHROPIC_API_KEY=sk-... ADMIN_PIN=1234 docker compose up --build
# API on :8000 against Postgres; run the frontend separately with npm run dev
```

## Using it

1. Open `/admin` (PIN `1234`), **Load orders**, publish a menu for the week.
2. A customer submits free text at `/order` (the menu shows there).
3. In `/admin`: parse orders, review the raw vs structured side by side, fix
   any `NEEDS REVIEW`, mark email-sent / delivered, see the overview table +
   revenue, and **Export CSV**.

## Config (backend/.env)

| Var | Default | Notes |
|-----|---------|-------|
| `DATABASE_URL` | `sqlite:///./app.db` | `postgresql+psycopg://…` for PG |
| `ANTHROPIC_API_KEY` | (none) | parsing disabled until set |
| `ANTHROPIC_MODEL` | `claude-opus-4-8` | |
| `ADMIN_PIN` | `1234` | **change before real use** |

## Tests

```bash
cd backend && .venv/bin/pytest      # 14 tests
cd frontend && npm run type-check
```
