# Spec: Order improvements (corrections, parse-all, email, pricing) + deploy prep

Builds on the order-submission / menus / parsing slices. Backend + admin only.

## 1. Correction flow (CLAUDE.md / order-parsing SKILL: "Dad fixes a misparse")
- `PATCH /api/admin/orders/{id}/items` (PIN) replaces an order's structured items
  with an admin-supplied set. Each item is re-matched to the menu (snapshotting
  price); status → `parsed`. The **raw text is never touched**.
- Every correction is logged to a new `order_corrections` table
  (`order_id`, `corrected_at`, `before_items` JSON, `after_items` JSON, `note`).

## 2. Parse all pending
- `POST /api/admin/orders/parse-pending` (PIN) parses every `pending_parse` order
  in one action (503 if no API key). Avoids per-order clicking and customer-facing
  latency. Per-order `POST .../{id}/parse` remains.

## 3. Order confirmation email
- `services/email.py` sends a confirmation via generic SMTP on submission;
  no-op when `SMTP_HOST` is unset, and never raises (delivery is best-effort, must
  not break submission). Sets `confirmation_email_sent` when actually sent.
- Config: `SMTP_HOST/PORT/USER/PASSWORD/FROM/USE_TLS`.

## 4. Pricing / totals
- `order_items.unit_price_cents` snapshots the matched menu item's price at match
  time (stable historical totals; money stays integer cents). `Order.total_cents`
  sums priced items. Exposed on `OrderRead`; shown per-order + as weekly revenue,
  and in the CSV.

## Admin dashboard (frontend)
`/admin/orders` adds: inline edit/correction of items, a "Parse all pending"
button, per-order totals + weekly revenue, and a Total column in the CSV.

## Data model / migrations
- Migration `9af23169fc6f`: add `order_items.unit_price_cents`; create
  `order_corrections`. Alembic `env.py` now uses batch mode only on SQLite, so
  migrations run natively on Postgres.

## Deploy readiness (#6 — added, not activated)
- `psycopg[binary]` driver; `backend/Dockerfile` (+ `.dockerignore`) running
  `alembic upgrade head` then uvicorn; root `docker-compose.yml` (Postgres + backend);
  comprehensive `backend/.env.example` and a root `README.md` (setup, changing the
  admin PIN, deploy). Frontend deploys separately via `NEXT_PUBLIC_API_URL`.

## Security note
Admin auth stays the shared PIN (`ADMIN_PIN`, env-driven so it's changeable) for
v1; real per-user login is the next security step before a wider launch.

## Out of scope
Online payment (confirmed not needed); real auth; actual deployment (artifacts are
ready, but provisioning hosts/DNS/secrets is the operator's step).
