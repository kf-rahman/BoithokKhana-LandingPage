# Implementation Strategy — Catering Order System v1 (Workflow 2)

Architecture per @api/.ai-knowledge/backend-architecture.md and
@web/.ai-knowledge/frontend-architecture.md. Async SQLAlchemy 2.x.

## Database
Engine: async SQLAlchemy. `DATABASE_URL` defaults to
`sqlite+aiosqlite:///./catering.db` (local, no Docker); deploy uses
`postgresql+asyncpg://…`. Alembic migrations run via a **sync** URL
derived from the same DB (sqlite / psycopg) — app async, migrations sync.
IDs are `sqlalchemy.Uuid` (native on PG, CHAR(32) on SQLite).

**Order**
- id: Uuid (pk)
- raw_text: str (not null, never overwritten)
- customer_name: str; customer_phone: str; customer_email: str|null
- structured_items: JSON|null  — `[{name, quantity, modifiers[], notes, matched: bool, unit_price_cents: int|null}]`
- delivery_date: date|null; delivery_notes: str|null
- item_confidence / delivery_confidence: Enum(high|medium|low)|null
- status: Enum(pending_parse|parsed|needs_review) default pending_parse
- unmatched_text: str|null
- menu_week_id: FK→MenuWeek|null (which week was active at parse time)
- confirmation_email_sent: bool=false; delivered: bool=false
- created_at: datetime UTC; corrected_at: datetime|null; correction_note: str|null
- total_cents: computed property from structured_items (int, never float)

**MenuWeek**
- id: Uuid; week_start_date: date; published: bool=false
- items: JSON — `[{name, price_cents}]`
- created_at: datetime UTC

## API (FastAPI, Pydantic v2 schemas, thin routers → services)
Public:
- POST /api/orders → persist raw + pending_parse, return OrderRead
- GET  /api/menus/current → latest published MenuWeek
Admin (header `X-Admin-Pin`, `require_admin` dependency, `ADMIN_PIN` env):
- GET  /api/admin/orders
- POST /api/admin/orders/{id}/parse ; POST /api/admin/orders/parse-pending
- PATCH /api/admin/orders/{id} → correction (structured_items) +/or flags
  (confirmation_email_sent, delivered); correction sets corrected_at/note
- POST /api/admin/menus → create/publish a week's menu
- GET  /api/admin/orders.csv → CSV export

## Services
- `order_parsing.py`: builds prompt from active MenuWeek + raw_text, calls
  Claude (`claude-opus-4-8`, structured output) via `asyncio.to_thread`
  around an isolated `_request_structured_parse` (mockable). Validates
  shape; matches item names to the week's menu (case-insensitive); sets
  unit_price_cents; computes status from confidence + unmatched + matches
  per @.ai/order-parsing.md. Persists raw BEFORE calling.
- `menus.py`: create/publish, get_current. `csv_export.py`: rows from
  structured_items. `orders.py`: create/list/correct/flags.

## Frontend (Next.js App Router, brand CSS from index.html)
- globals.css: lift the exact `:root` brand vars + component classes from
  `index.html`; Tailwind preflight off; Font Awesome via CDN.
- components/Header.tsx (Home | Menu | Order).
- app/order/page.tsx — Client Component: name/phone/email + free-text;
  shows current menu; confirmation state (no redirect); error/loading.
- app/admin/page.tsx — Client Component (PIN gate + interactivity): order
  cards with raw | structured **side by side**; `needs_review` visually
  distinct (red card, not a small badge); inline correction editor;
  "confirm delivery date" prompt when delivery_confidence=low; menu
  publish form; CSV export; empty/loading/error states.

## Testing
pytest + pytest-asyncio, httpx ASGI transport, in-memory/temp SQLite,
parser mocked via `_request_structured_parse`. Cases = TRD criterion 10.

## Open questions
None blocking. Admin auth resolved (shared PIN via env). Deployment
artifacts (Dockerfile/compose) added at the end for parity with WF1.
