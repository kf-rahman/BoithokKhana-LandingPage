# Boithok Khana — Order System

Replaces the manual WhatsApp + Excel ordering workflow for a family-run weekly
catering business: customers submit an order in plain text, it's parsed into
structured items against the published weekly menu, and Dad manages everything
from an admin dashboard.

- `index.html` — the existing marketing landing page (served via GitHub Pages). **Left untouched.**
- `frontend/` — Next.js app (App Router, TypeScript) — order form + admin.
- `backend/` — FastAPI + SQLAlchemy + Alembic.
- `docs/` — per-feature stories & specs; `docs/pr-checklist.md` is the review gate.

## What it does
- **Customer** submits a free-text order at `/order`.
- **Parser** (Claude API) turns the text into structured line items, matched to
  the published menu; anything unmatched / low-confidence / failed → `needs_review`
  (never invented; the raw text is never altered).
- **Admin** (`/admin`, PIN-protected): publish the weekly menu, view orders (raw
  vs. structured side by side), correct a misparse, parse pending orders, toggle
  email-sent / delivered, see the weekly quantity grid + revenue, and export CSV.

---

## Local development

### Backend
```sh
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit .env (see below)
alembic upgrade head          # creates the SQLite dev DB
uvicorn app.main:app --reload # http://localhost:8000  (docs at /docs)
pytest                        # run the test suite
```

### Frontend
```sh
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                        # http://localhost:3000
```

## Configuration (`backend/.env`)
All config is environment-driven (see `backend/.env.example`):

| Var | Purpose |
|---|---|
| **`ADMIN_PIN`** | **The admin password.** Change it anytime — set this and restart the backend. Default `change-me`. |
| `DATABASE_URL` | `sqlite:///./boithok.db` locally; `postgresql+psycopg://…` in production. |
| `ANTHROPIC_API_KEY` | Enables order parsing. Without it, parse endpoints return 503. |
| `ANTHROPIC_MODEL` | Parser model (default `claude-opus-4-8`). |
| `CORS_ORIGINS` | JSON array of allowed frontend origins. |
| `SMTP_*` | Order-confirmation email; leave `SMTP_HOST` blank to disable. |

> **Changing the admin password** is just `ADMIN_PIN` in the environment — no code
> change. The auth lives in one dependency (`app/api/deps.py`), so swapping the
> shared PIN for real per-user login later is a contained change.

---

## Deployment (ready when you are)

The frontend and backend deploy independently.

- **Backend + Postgres (Docker):**
  ```sh
  # set secrets in a root .env (gitignored): ADMIN_PIN, ANTHROPIC_API_KEY, SMTP_*, ...
  docker compose up --build
  ```
  The backend container runs `alembic upgrade head` on start, so the Postgres
  schema is created automatically. Or deploy the backend image to any host
  (Railway/Render/Fly) with a managed Postgres and the env vars above.

- **Frontend (Vercel or similar):** deploy `frontend/` and set
  `NEXT_PUBLIC_API_URL` to the backend's public URL.

- **Where it lives:** the marketing site stays on `boithokkhana.ca`; a natural
  home for this app is a subdomain like `order.boithokkhana.ca` (set that in
  `CORS_ORIGINS`).

### Before a real client launch
- Set a strong `ADMIN_PIN` (and consider real per-user login).
- Use a real email provider with SPF/DKIM on the domain.
- Turn on automated Postgres backups.
- Keep all secrets in the host's secret manager (never in git).
