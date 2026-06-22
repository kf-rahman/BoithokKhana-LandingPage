# Boithok Khana — Order System (Workflow 2 build)

Free-text catering orders, parsed by Claude into structured line items,
managed from a PIN-protected admin dashboard. This branch (`workflow2`)
is the Softcery-workflow build; `workflow-1` is the software-factory build
of the same product.

## Run locally (no Docker)

The backend defaults to SQLite, so nothing else is needed.

```bash
# backend  →  http://localhost:8000
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env          # then add your ANTHROPIC_API_KEY, set ADMIN_PIN
.venv/bin/uvicorn app.main:app --reload

# frontend →  http://localhost:3000
cd frontend
npm install
npm run dev
```

Tables are created automatically on first start. To use Alembic instead:
`cd backend && .venv/bin/alembic upgrade head`.

## Run with Postgres (Docker Compose)

```bash
ANTHROPIC_API_KEY=sk-... ADMIN_PIN=1234 docker compose up --build
# API on :8000 against Postgres; run the frontend separately with npm run dev
```

## Using it

1. Open `/admin`, enter the PIN, **Load orders**, then publish a menu for
   the week (dish names + prices).
2. A customer submits free text at `/order` (the menu is shown there).
3. In `/admin`, **Parse** an order (or **Parse all pending**). The raw text
   and the structured parse sit side by side. Anything uncertain is flagged
   **NEEDS REVIEW** — fix it inline; the raw text is never changed.
4. **Export CSV** for prep/shopping.

## Config (backend/.env)

| Var | Default | Notes |
|-----|---------|-------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./catering.db` | `postgresql+asyncpg://…` for PG |
| `ANTHROPIC_API_KEY` | (none) | parsing is disabled until set |
| `ANTHROPIC_MODEL` | `claude-opus-4-8` | |
| `ADMIN_PIN` | `1234` | **change before real use** |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | JSON list |

## Tests

```bash
cd backend && .venv/bin/pytest      # 12 tests
cd frontend && npm run type-check
```
