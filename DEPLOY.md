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

## 3. Production — Render, one domain

Everything lives on **one hostname**, `www.boithokkhana.ca`:

| Path        | Served by                                                  |
|-------------|------------------------------------------------------------|
| `/`         | the marketing site (root `index.html`)                     |
| `/order`    | the customer order form                                    |
| `/admin`    | Dad's dashboard                                            |
| `/api/*`    | proxied to the FastAPI backend (private, no public URL)    |

The browser only ever talks to one origin, so **there is no CORS involved**
and the backend never needs its own subdomain. The proxy is
`frontend/app/api/[...path]/route.ts` — a route handler, not a `next.config`
rewrite, because rewrites are frozen at build time and the backend's address
is only known at runtime.

> **On the free plan the proxy uses the API's public URL.** Render's private
> network won't work here: free web services can send private requests but
> cannot *receive* them, so `boithok-api:10000` is unreachable and the proxy
> 502s. Once `boithok-api` is on a paid plan, switch `BACKEND_ORIGIN` back to
> the private address (commented in `render.yaml`) so API traffic stops
> crossing the public internet.

`render.yaml` in the repo root declares all three services, so Render creates
them for you rather than you clicking through forms.

### Step 1 — deploy the services

1. Push this branch to GitHub.
2. Go to <https://dashboard.render.com> → **New** → **Blueprint**.
3. Connect the `kf-rahman/BoithokKhana-LandingPage` repo and pick this branch.
4. Render reads `render.yaml` and shows three resources: `boithok-db`,
   `boithok-api`, `boithok-web`. It will prompt for the secrets marked
   `sync: false`:
   - `ADMIN_PIN` — **change it from 1234.** This is the only thing standing
     between the public and every customer's order.
   - `ANTHROPIC_API_KEY` — order parsing stays off without it (orders still
     save as `pending_parse`, nothing is lost).
   - `SENTRY_DSN` / `NEXT_PUBLIC_SENTRY_DSN` — leave blank for now, see §4.
5. **Apply**. First build takes ~5–10 minutes. Migrations run automatically on
   the API's start command.

### Cost — free to start, but read this

`render.yaml` uses **free** plans, so no card is required. Two limits matter:

- **Free web services sleep after 15 minutes idle** and take ~50 seconds to
  wake. A customer hitting a cold order page waits, or gives up.
- **Free Postgres is deleted 30 days after it's created.** The orders in it go
  with it. Render emails a warning first.

That's fine for testing. **Before Dad relies on this for real orders**, in the
Render dashboard upgrade `boithok-db` to `basic-256mb` (~$6/mo) and the two
services to `starter` (~$7/mo each). Custom domains work on free plans, so the
domain setup below doesn't change.

### Step 2 — point the domain (GoDaddy)

In Render, open **boithok-web → Settings → Custom Domains**. It shows the
exact values to use. Then in GoDaddy → **My Products → boithokkhana.ca →
DNS → Manage DNS**:

| Type    | Name  | Value                            | Notes                        |
|---------|-------|----------------------------------|------------------------------|
| `CNAME` | `www` | `boithok-web.onrender.com`       | exact value from Render      |
| `A`     | `@`   | Render's apex IP (shown in UI)   | makes the bare domain work   |

Delete any existing `www` record pointing at GitHub Pages first — that's what
currently serves the old site, and both can't win.

DNS takes 10–60 minutes. Render issues the HTTPS certificate automatically
once it resolves; until then you'll see a certificate warning, which is
expected and self-resolving.

> The old GitHub Pages site keeps working until you change that `www` record.
> That is the actual cutover moment — everything before it is reversible.

### Step 3 — first run

1. Visit `https://www.boithokkhana.ca` — the marketing site.
2. Go to `/admin` → enter the PIN → **publish the first weekly menu**. Until
   a menu is published, `/order` has nothing to show.
3. Place a test order through `/order`, then confirm it appears in `/admin`
   with the raw text intact.

## 4. Error reporting (Sentry)

Wired in and **inert until you set a DSN** — safe to deploy as-is.

Sentry's free tier (5k errors/month, no card) is enough for this app.

1. Create a project at <https://sentry.io> — pick **FastAPI** for the backend
   and **Next.js** for the frontend (two projects, or one, your call).
2. Copy each DSN from **Settings → Client Keys (DSN)**.
3. In Render, set the env vars and redeploy. Note there are **two DSNs but
   three fields** — the frontend runs both in the browser and on the server,
   and each reads a differently-named var:

   | Render service | Env var                  | Value                    |
   |----------------|--------------------------|--------------------------|
   | `boithok-api`  | `SENTRY_DSN`             | the FastAPI project's DSN |
   | `boithok-web`  | `NEXT_PUBLIC_SENTRY_DSN` | the Next.js project's DSN |
   | `boithok-web`  | `SENTRY_DSN`             | the Next.js DSN **again** |

   The last two are the same value. Setting only `NEXT_PUBLIC_SENTRY_DSN`
   catches browser errors but silently misses every server-side crash.
   `NEXT_PUBLIC_*` is inlined at build time, so it needs a **redeploy**, not
   just a restart.

**What is deliberately not sent:** customer order text. `send_default_pii` is
off, request bodies and cookies are dropped, and `backend/app/observability.py`
redacts `raw_text`, names, phones, emails and delivery notes from stack
frames. Session replay is disabled for the same reason. You get the stack
trace, not the customer's personal information.

Local test that reporting works:

```bash
cd backend && SENTRY_DSN='<dsn>' uvicorn app.main:app
```
