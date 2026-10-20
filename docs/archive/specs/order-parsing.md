# Spec: Order parsing (raw text → structured items)

Implements docs/stories/order-parsing.md. Follows the contract in
`.claude/skills/order-parsing/SKILL.md`. Backend-only.

## Flow
1. Order already persisted with `raw_text` + status `pending_parse`
   (order-submission slice).
2. Admin triggers `POST /api/admin/orders/{id}/parse` (PIN-gated).
3. Service stamps `order.menu_id` = the active **published** menu.
4. Service calls Claude server-side with the published menu as context + the raw
   text, requesting structured output (the SKILL's schema).
5. Each parsed item → an `OrderItem` row; matched to a `menu_item` by name
   (case-insensitive) → `menu_item_id`, else `null`. Modifiers + notes are
   combined into `OrderItem.notes`.
6. Status: `parsed` if confidence high/medium AND every item matched AND no
   leftover `unmatched_text` AND a menu exists; otherwise `needs_review`.
7. `raw_text` is never modified. Re-parse clears prior `order_items`, never the
   raw text.

## Claude integration
- Official `anthropic` Python SDK; `client.messages.parse(output_format=ParsedOrder)`
  (structured outputs — guarantees schema-valid result).
- Model: `settings.anthropic_model` (default `claude-opus-4-8`).
- Key: `settings.anthropic_api_key` (`ANTHROPIC_API_KEY`). If unset → endpoint
  returns **503** (a config error; the order is left untouched, not flagged).
- Prompt: a system prompt listing THIS WEEK'S published menu items + the SKILL
  rules (match to the menu; never invent; ambiguous → `unmatched_text` + lower
  confidence). The raw order text is the user message.
- `ParsedOrder` (per SKILL): `items[{name, quantity, modifiers[], notes?}]`,
  `delivery_date?`, `delivery_notes?`, `confidence (high|medium|low)`,
  `unmatched_text?`. The whole call lives in `services/order_parsing.py`; the
  one Claude-calling function is isolated so it can be mocked in tests.

## Data model
No schema change — uses the existing `order_items`, `orders.menu_id`,
`confidence`, `unmatched_text`, `delivery_*`, `parsed_at`, `status`.

## API
### `POST /api/admin/orders/{order_id}/parse`  (auth: shared admin PIN)
- **200** `OrderRead` — `status` `parsed`|`needs_review`, `items` populated,
  parse fields set.
- **404** if the order doesn't exist.
- **503** if `ANTHROPIC_API_KEY` is not configured.

## Failure handling (per SKILL — never a silent failure)
- API error or schema-invalid output → `order.status = needs_review`, `parsed_at`
  set, raw text intact, **no** invented items.
- Missing API key → 503, order untouched.

## Out of scope
Auto-parse on submission; admin review/correction UI; pricing.
