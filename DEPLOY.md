# Deploying Boithok Khana (order app)

The app is two deployable pieces plus a database:

- **Frontend** — Next.js (`frontend/`). Static-ish Node server; deploys to
  Vercel or any Node host, or the provided `frontend/Dockerfile`.
- **Backend** — FastAPI (`backend/`). Containerised via `backend/Dockerfile`;
  applies Alembic migrations on start.
- **Database** — PostgreSQL in production (SQLite locally, no setup).

> This is the order app, separate from the marketing site (`index.html`, served
> via GitHub Pages / `CNAME`). The order app can't run on GitHub Pages — it
> needs a Python backend + a database.

## 1. Local dev (fastest, no Docker)

```bash
# backend — SQLite, no key needed (orders save as pending_parse)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head        # or it auto-creates tables on first boot
python seed.py              # a sample published menu for testing
uvicorn app.main:app --reload   # http://localhost:8000

# frontend (separate shell)
cd frontend
npm install
npm run dev                 # http://localhost:3000
```

Admin dashboard: http://localhost:3000/admin → enter the PIN (`ADMIN_PIN`,
default `1234`).

## 2. Full stack locally (Docker Compose)

Brings up Postgres + API (:8000) + web (:3000) together:

```bash
cp env.example .env         # then edit: ADMIN_PIN, ANTHROPIC_API_KEY, ...
docker compose up --build
```

`NEXT_PUBLIC_API_URL` defaults to `http://localhost:8000` (the browser reaches
the API on the host's published port). Seed a menu once the stack is up:

```bash
docker compose exec backend python seed.py
```

## 3. Production hosting (host not yet chosen)

Recommended split for a small app:

| Piece    | Host                          | Notes                                            |
|----------|-------------------------------|--------------------------------------------------|
| Frontend | Vercel                        | Set `NEXT_PUBLIC_API_URL` to the backend URL.    |
| Backend  | Render / Railway / Fly.io     | Build from `backend/Dockerfile`.                 |
| Database | Managed Postgres (same host)  | Set `DATABASE_URL=postgresql+psycopg://…`.       |

### Required backend environment

| Var                 | Purpose                                             |
|---------------------|-----------------------------------------------------|
| `DATABASE_URL`      | `postgresql+psycopg://user:pass@host:5432/db`       |
| `ADMIN_PIN`         | **Change from the default** — protects `/admin`.    |
| `ANTHROPIC_API_KEY` | Enables live order parsing (else orders stay pending). |
| `ANTHROPIC_MODEL`   | Defaults to `claude-opus-4-8`.                      |
| `CORS_ORIGINS`      | JSON array incl. the deployed frontend URL, e.g. `["https://order.boithokkhana.ca"]`. |
| `SMTP_*`            | Optional — order-confirmation emails (blank = off). |

### Deploy checklist

1. Provision Postgres; set `DATABASE_URL`.
2. Deploy the backend image (it runs `alembic upgrade head` on start).
3. Set a strong `ADMIN_PIN` and the real `ANTHROPIC_API_KEY`.
4. Set `CORS_ORIGINS` to the frontend's URL.
5. Deploy the frontend with `NEXT_PUBLIC_API_URL` → the backend URL.
6. Publish the first weekly menu from `/admin/menu`.
