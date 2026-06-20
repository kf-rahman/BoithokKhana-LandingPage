# Spec: Menus + structured orders (data model)

Builds on docs/specs/order-submission.md. This slice is the **database foundation
only** — no UI, no parser, no menu-publishing logic. Those are separate features
that build on these tables.

Implements the "line items + auto weekly grid" decision: dishes are stored as
**rows**, never columns, so a changing weekly menu never changes the schema.

## Tables

### `menus` — one row per published week ("the menu we publish")
- `id` PK
- `week_of` Date, indexed — the week this menu is for (the "id mapped to time")
- `status` str(20) — `draft | published | archived`, default `draft`
- `published_at` datetime(tz), nullable
- `created_at` / `updated_at` datetime(tz), UTC

### `menu_items` — the dishes on a menu (source of truth for validation)
- `id` PK
- `menu_id` FK → `menus` (ON DELETE CASCADE), indexed
- `name` str(120)
- `price_cents` int — **money is integer cents, never float**
- `active` bool, default true
- `created_at` / `updated_at`

### `orders` — extended
- **+ `customer_email`** str(255), **nullable at DB / REQUIRED at the API**
  (`OrderCreate`). Nullable so the column dropped onto existing rows cleanly;
  every new order has a validated email.
- **+ `menu_id`** FK → `menus`, nullable, indexed — which week's menu was active
  when the order was placed (stamped later, at submission, once menus exist).
- **+ `confirmation_email_sent`** bool, default false — toggled in the admin view.
- **+ `delivered`** bool, default false — toggled in the admin view.
- **− `structured_items`** (JSON) dropped — replaced by `order_items` rows.
- unchanged: `raw_text` (never overwritten), `status`
  (`pending_parse|parsed|needs_review`), `delivery_date/notes`, `confidence`,
  `unmatched_text`, `parsed_at`, timestamps.

### `order_items` — the structured order, one row per dish
- `id` PK
- `order_id` FK → `orders` (ON DELETE CASCADE), indexed
- `menu_item_id` FK → `menu_items`, **nullable**, indexed — NULL means the item
  matched nothing on the active menu → the order is flagged for review rather
  than inventing an item (CLAUDE.md non-negotiable).
- `item_name` str(120) — as parsed from the raw text
- `quantity` int, default 1
- `notes` text, nullable
- `created_at`

## Relationships
- `Menu` 1—* `MenuItem` (cascade delete)
- `Order` 1—* `OrderItem` (cascade delete)
- `OrderItem` *—1 `MenuItem` (the optional match link)
- `Order` *—1 `Menu` (the menu active at order time)

## Why menu changes never touch the schema
A new week = new `menus` row + `menu_items` rows. A customer order = `order_items`
rows. The admin's weekly grid is computed **at display time** from that week's
`menu_items` (columns) joined to `order_items` (quantities). Storage shape is
constant; only the rendered grid changes.

## Migrations
- `81176b5b1dbd` — create `menus`, `menu_items`, `order_items`; add
  `orders.customer_email` + `orders.menu_id`; drop `orders.structured_items`.
  Operation order hand-tuned for SQLite safety (alter `orders` before
  `order_items` exists). Reversible. Existing order row preserved.
- `a2447c7b056b` — add `orders.confirmation_email_sent` + `orders.delivered`
  (backfilled false on existing rows).
- `alembic check` reports no drift; both verified up/down.

## Out of scope (next features, in suggested order)
1. Connect the `/order` form (frontend) to `POST /api/orders` + the new email field.
2. Menu-publishing admin (create/publish this week's menu).
3. Stamp new orders with the active `menu_id` at submission.
4. Parser: `raw_text` → `order_items`, validated against the published menu.
5. Admin order view: weekly grid + toggling `confirmation_email_sent`/`delivered`
   + CSV export.

## Open (must resolve before the admin view)
- Admin authentication (shared PIN vs. real login) — flagged per CLAUDE.md.
