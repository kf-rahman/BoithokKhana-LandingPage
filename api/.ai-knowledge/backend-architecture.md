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
  structured_items: JSON (nullable until parsed)
  delivery_date: date (nullable)
  delivery_notes: str (nullable)
  item_confidence: enum(high, medium, low) (nullable until parsed)
  delivery_confidence: enum(high, medium, low) (nullable until parsed)
  status: enum(pending_parse, parsed, needs_review)
  menu_week_id: FK -> MenuWeek (which week's menu was active at parse time)
  customer_name: str
  customer_contact: str
  created_at: datetime (UTC)
  corrected_at: datetime (nullable — set when Dad edits structured_items)
  correction_note: str (nullable — what changed and why, if corrected)

MenuWeek
  id: UUID
  week_start_date: date
  items: JSON (the list of dishes available that week)
```

## Why menu_week_id exists

A correction made weeks later needs to be understood against the menu
that was actually active when the order was placed, not whatever menu
is active now. Don't drop this FK even if it seems redundant early on.

## Update this file when

- A new top-level model is added.
- An existing model's fields change in a way that affects how other
  services query it.
- A new service is added to `services/`.
