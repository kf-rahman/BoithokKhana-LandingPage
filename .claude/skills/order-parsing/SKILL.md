---
name: order-parsing
description: The contract for converting a customer's free-text order into structured order data using the Claude API. Load this whenever implementing, modifying, or testing anything related to order parsing, the Order model's raw-text vs structured fields, or the "needs manual review" flow.
---

# Order Parsing — Domain Contract

This is the single source of truth for how free-text orders become
structured data. Backend-builder, test-verifier, and
implementation-validator should all defer to this file rather than
reinventing the contract per-feature.

## Why this is hard (and why it's not a regex problem)

The weekly menu changes every week and items mix and match
("2 chicken biryani, 1 veg thali extra spicy, no onions on the biryani,
deliver friday evening"). A fixed dropdown can't represent this. A naive
keyword match will misparse modifiers ("no onions") as separate items.
This is why parsing is LLM-backed rather than rule-based.

## The non-negotiable rule

**The original raw text is never discarded, never overwritten, and is
always stored permanently alongside whatever structured data is
derived from it.** Every Order record has both fields. If the parse is
later corrected by Dad, the raw text field is untouched — only the
structured field changes, and the correction itself should be
logged (who/when/what changed), not silently overwritten.

## High-level flow

1. Customer submits free text via the order form.
2. Backend receives the raw text, immediately persists an Order row with
   the raw text and a status of `pending_parse` — persistence of raw
   text happens BEFORE the parse call, not after, so a parsing failure
   or API outage never loses a customer's order.
3. Backend calls the Claude API with the current week's menu as context
   plus the raw order text, requesting structured output.
4. Backend evaluates the model's confidence (see below) and sets order
   status to either `parsed` or `needs_review`.
5. Admin dashboard displays both `raw_text` and `structured_items` for
   every order, regardless of status — status is a flag/badge, not a
   reason to hide either field.

## Structured output shape (target schema)

```json
{
  "items": [
    {
      "name": "string — should match a current menu item where possible",
      "quantity": "integer",
      "modifiers": ["string", "..."],
      "notes": "string or null — anything that didn't fit modifiers cleanly"
    }
  ],
  "delivery_date": "ISO date string or null if not specified",
  "delivery_notes": "string or null",
  "confidence": "high | medium | low",
  "unmatched_text": "string or null — any part of the original text the model could not map to a structured field"
}
```

## Confidence handling

- **high** → status `parsed`, shown normally in the dashboard.
- **medium** → status `parsed`, but visually flagged in the dashboard
  ("double-check this one") — still usable for prep, but worth a glance.
- **low**, or any non-empty `unmatched_text`, or any item name that
  doesn't match a current menu item → status `needs_review`. These
  orders must be visually distinct in the admin dashboard (not just a
  small badge — Dad needs to immediately see these need attention before
  prep day).

## Prompting the model

- Always include the current week's menu as context in the prompt. The
  model should not be parsing in a vacuum — matching against real items
  in this week's menu is what makes "biryani" resolve to the correct
  specific dish rather than a guess.
- Explicitly instruct the model: if an item, quantity, or modifier is
  ambiguous, do NOT guess — put it in `unmatched_text` and lower
  confidence rather than inventing a plausible-sounding structured value.
  This directly enforces the project's "never invent order items"
  non-negotiable from CLAUDE.md.
- Request structured JSON output; validate it against the schema above
  server-side before persisting. If the model's output fails schema
  validation, treat this the same as a low-confidence parse —
  `needs_review`, never a silent failure.

## What backend-builder should implement

- A `services/order_parsing.py` service encapsulating the Claude API
  call, prompt construction (including current menu context), and
  response validation. Route handlers should call this service, not
  build prompts inline.
- Persist raw text first, in its own transaction/step, before attempting
  the parse — per the non-negotiable above.
- Store the menu context used at parse time alongside the order (or a
  reference to which week's menu was active), so a later correction by
  Dad can be understood in context even after the menu changes.

## What test-verifier should specifically test

- A high-confidence order parses correctly end to end.
- A genuinely ambiguous order (e.g. an item not on the current menu)
  results in `needs_review` status, not a guessed structured value.
- Raw text survives unchanged even after Dad corrects the structured
  fields.
- A simulated parsing/API failure still results in the raw text being
  persisted (never lost), with status reflecting the failure.
