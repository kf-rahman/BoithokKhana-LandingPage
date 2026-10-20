# Spec: Order submission (raw-text-first persistence)

Implements: docs/stories/order-submission.md

## Data model

New SQLAlchemy model `Order` (table `orders`) in `backend/app/models/order.py`:

| column | type | null | notes |
|---|---|---|---|
| id | Integer PK | no | autoincrement |
| customer_name | String(120) | no | trimmed at the schema boundary |
| customer_phone | String(40) | no | trimmed at the schema boundary |
| raw_text | Text | no | the customer's free text, stored **verbatim**; never overwritten/discarded |
| status | String(20) | no | `OrderStatus` enum stored as string; default `pending_parse` |
| structured_items | JSON | yes | filled later by the parser (shape per order-parsing SKILL) |
| delivery_date | Date | yes | parsed later |
| delivery_notes | Text | yes | parsed later |
| confidence | String(10) | yes | `high`/`medium`/`low`, parsed later |
| unmatched_text | Text | yes | parsed later |
| parsed_at | DateTime(tz) | yes | set when parsed |
| created_at | DateTime(tz) | no | server default `now()` (UTC) |
| updated_at | DateTime(tz) | no | server default `now()`, `onupdate now()` (UTC) |

- `OrderStatus` = `pending_parse | parsed | needs_review` (string-backed enum so it
  is portable across SQLite and Postgres without a native enum type).
- All structured/parsed columns are **nullable now** so the parsing feature needs
  no destructive migration later.
- Timestamps stored UTC via `DateTime(timezone=True)`; display-time localization
  is a presentation concern handled later (CLAUDE.md timezone rule).
- No money fields in this slice (prices come with the menu feature).

Pydantic schemas (`backend/app/schemas/order.py`):
- `OrderCreate` (request): `customer_name` (1–120, trimmed, non-blank),
  `customer_phone` (1–40, trimmed, non-blank), `raw_text` (non-blank — rejected if
  empty/whitespace-only, but stored **unchanged**, not trimmed).
- `OrderRead` (response, `from_attributes`): `id, customer_name, customer_phone,
  raw_text, status, structured_items, delivery_date, delivery_notes, confidence,
  unmatched_text, created_at, updated_at`.

## API contract

### `POST /api/orders`
- **Request (JSON):** `{ "customer_name": str, "customer_phone": str, "raw_text": str }`
- **Response (success) `201 Created`:** `OrderRead` — includes `id`,
  `status: "pending_parse"`, `raw_text` echoed verbatim, structured fields `null`.
- **Response (error) `422 Unprocessable Entity`:** validation failure (missing or
  blank `raw_text`, `customer_name`, or `customer_phone`). No row is persisted.
- **Auth:** none — this is the public customer order submission. (No admin/read
  endpoints exist in this slice, so the unresolved admin-auth decision is not
  engaged here.)

No other endpoints this slice. Reading/listing orders is deferred to the
admin-dashboard feature.

## UI states

N/A this slice (backend-only). Recorded for the later frontend-wiring slice so it
isn't lost: submitting → loading; `201` → success confirmation echoing the order;
`422` → inline validation error **without** clearing the typed text; network/5xx →
"couldn't submit, please try again" while preserving what the customer typed.

## Parsing/business logic notes

Parsing is OUT of scope here. Per `.claude/skills/order-parsing/SKILL.md`, raw text
is persisted **before** any parse attempt; this slice implements exactly that first
step — persist raw text, set status `pending_parse`. The parser (next feature) will
pick up `pending_parse` orders, populate the structured columns, and set
`parsed`/`needs_review`, all **without** touching `raw_text`. The persistence layer
is centralized in `services/orders.py` so the parser slice extends it rather than
duplicating it.

## Persistence / infra

- SQLAlchemy 2.0 ORM. Engine from `settings.database_url`; default
  `sqlite:///./boithok.db` for local dev (Docker/Postgres deferred per the user).
  Postgres swap = change `DATABASE_URL` only; column types chosen to be portable
  (JSON, Date, `DateTime(timezone=True)`, string-backed enum).
- Alembic migration creates the `orders` table (`backend/alembic/`). `alembic
  upgrade head` applies it. The SQLite file is gitignored; migrations are committed.
- `get_db` FastAPI dependency yields a session; the route handler stays thin and
  delegates to `services/orders.py`.

## Out of scope

Carried from the story: LLM parsing; admin read/list/correction/CSV; frontend
wiring; pricing.

## Open questions

None blocking. Documented calls (grounded in earlier user direction — "no Docker
yet", and the order form already shows name + phone + free-text):

1. **SQLite locally**, kept Postgres-swappable.
2. **Submission collects only name + phone + raw_text.** Delivery date/details live
   inside the free text and are extracted by the parser later — not separate inputs.
3. **POST-only this slice** (no read endpoints), which keeps the admin-auth decision
   out of scope.

If you'd prefer different submission fields, or want read-back endpoints now, say so
and I'll fold it in.
