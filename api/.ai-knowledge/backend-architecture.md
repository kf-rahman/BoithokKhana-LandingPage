# Backend Architecture

## Layout

```
backend/
  app/
    api/        route handlers — thin, no business logic
    models/     SQLAlchemy models
    schemas/    Pydantic request/response schemas
    services/   business logic (order parsing, CSV export, etc.)
    db/         session/engine setup
  alembic/      migrations
  tests/
```

## Core data model (current)

```
Order
  id: UUID
  raw_text: str (never null after creation, never overwritten)
  customer_name: str
  customer_phone: str
  customer_email: str (nullable)
  structured_items: JSON (nullable until parsed)
    -> [{name, quantity, modifiers[], notes, matched, unit_price_cents}]
  delivery_date: date (nullable)
  delivery_notes: str (nullable)
  item_confidence: str high|medium|low (nullable until parsed)
  delivery_confidence: str high|medium|low (nullable until parsed)
  status: str pending_parse|parsed|needs_review
  unmatched_text: str (nullable — text the parser could not place)
  menu_week_id: FK -> MenuWeek (which week's menu was active at parse time)
  confirmation_email_sent: bool ; delivered: bool
  created_at: datetime (UTC)
  corrected_at: datetime (nullable — set when Dad edits structured_items)
  correction_note: str (nullable — what changed and why, if corrected)
  total_cents: int (computed property — sum of matched line items)

MenuWeek
  id: UUID
  week_start_date: date
  published: bool
  items: JSON (the dishes available that week: [{name, price_cents}])
  created_at: datetime (UTC)
```

Note: the original sketch had a single `customer_contact`; the build uses
separate name/phone/email (a real product requirement). Enums are stored as
validated strings (Pydantic enforces the allowed values at the API boundary)
to keep cross-dialect migrations simple. Money is integer cents only.

## Why menu_week_id exists

A correction made weeks later needs to be understood against the menu
that was actually active when the order was placed, not whatever menu
is active now. Don't drop this FK even if it seems redundant early on.

## Update this file when

- A new top-level model is added.
- An existing model's fields change in a way that affects how other
  services query it.
- A new service is added to `services/`.
