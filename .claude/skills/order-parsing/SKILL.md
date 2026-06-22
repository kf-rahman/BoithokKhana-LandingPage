---
name: order-parsing
description: Domain contract for converting a customer's free-text order into structured data via the Claude API. Load when implementing, modifying, or testing anything related to order submission, parsing, confidence handling, or the raw-text/structured-data display in the admin dashboard.
---

# Order Parsing — Domain Contract

## Flow

1. Customer submits free text.
2. Backend persists an `Order` row with raw text and status
   `pending_parse` **before** attempting to parse. A parsing failure or
   API outage must never lose the customer's order.
3. Backend calls the Claude API with the current week's menu as context
   plus the raw text, requesting structured JSON.
4. Backend validates the response against the schema below and sets
   status to `parsed` or `needs_review`.
5. Admin dashboard always shows raw text and structured data together,
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

## Confidence → status

- `item_confidence: high` → `parsed`, shown normally.
- `item_confidence: medium` → `parsed`, flagged for a glance.
- `item_confidence: low`, non-empty `unmatched_text`, or an item that
  doesn't match the current week's menu → `needs_review`, visually
  distinct in the dashboard (not a small badge).
- `delivery_confidence: low` doesn't trigger `needs_review` on its own —
  it surfaces a separate "confirm delivery date" prompt, since date
  ambiguity and item ambiguity fail differently and need different UI
  treatment.

## Prompting rule

Always pass the current week's menu as context. Explicitly instruct the
model not to guess — ambiguous items, quantities, or modifiers go into
`unmatched_text` with lowered confidence rather than being resolved
silently. Validate the response against the schema server-side; a
schema-invalid response is treated as `needs_review`, never a silent
failure.

## Testing this

- High-confidence order parses end to end correctly.
- An order referencing an item not on the current menu results in
  `needs_review`, not a guessed match.
- Raw text is unchanged after Dad corrects the structured fields.
- A simulated API failure still results in the raw text being
  persisted.
