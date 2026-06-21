# Order Parsing — Domain Contract

The hardest problem in this project. Read this before touching anything
related to order submission, parsing, or the admin dashboard's
raw/structured display.

## Why this needs an LLM, not regex

The menu changes weekly and items mix and match in free text. A fixed
dropdown or keyword match can't represent "2 chicken biryani no spice, 1
veg thali, extra rice" reliably — "no spice" and "extra rice" are
modifiers, not separate items, and which dish "biryani" refers to
depends on what's actually on this week's menu.

## Flow

1. Customer submits free text.
2. Backend persists an Order row with raw text and status `pending_parse`
   **before** attempting to parse — a parsing failure must never lose
   the customer's order.
3. Backend calls the Claude API with the current week's menu as context
   plus the raw text, requesting structured JSON output (schema below).
4. Backend validates the response against the schema and sets status to
   `parsed` or `needs_review` based on confidence.
5. Admin dashboard always shows both raw text and structured data,
   regardless of status.

## Structured output schema

```json
{
  "items": [
    {"name": "string", "quantity": "integer", "modifiers": ["string"], "notes": "string|null"}
  ],
  "delivery_date": "ISO date or null",
  "delivery_notes": "string or null",
  "item_confidence": "high | medium | low",
  "delivery_confidence": "high | medium | low",
  "unmatched_text": "string or null"
}
```

Note: item confidence and delivery confidence are tracked separately
(see @.ai/sessions/ for why, once that session log exists) — they fail
in different ways and deserve different UI treatment.

## Rule: never guess

If the model is uncertain about an item, quantity, or modifier, it must
return that text in `unmatched_text` and lower `item_confidence` rather
than producing a plausible-but-invented structured value. This is
enforced by explicit prompt instruction and schema validation
server-side — never trust the model's confidence claim without
validating its output shape too.

## Confidence → UI behavior

- `item_confidence: high` → status `parsed`, shown normally.
- `item_confidence: medium` → status `parsed`, flagged for a glance.
- `item_confidence: low`, or non-empty `unmatched_text`, or an item name
  that doesn't match the current week's menu → status `needs_review`,
  visually distinct (not a small badge) in the dashboard.
- `delivery_confidence: low` → doesn't block the order into
  `needs_review`; instead surfaces a "confirm delivery date" prompt in
  the admin view.
