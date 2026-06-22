# Spec: Customer order submission

## Goal

Let a customer submit a food order as free text (no dropdowns) and have
it reliably stored, replacing the current WhatsApp-texting-Dad flow.

## Constraints

- Raw text must be persisted before any parsing is attempted — see
  AGENTS.md non-negotiable #1 and the order-parsing skill.
- This spec covers submission and storage only. Parsing happens here
  too (it's one flow), but the admin display of parsed results is a
  separate feature/spec.

## Acceptance criteria

- [ ] A customer can reach `/order`, see the current week's menu for
      reference, and type their order as free text in a textarea.
- [ ] Submitting with empty text is blocked client-side with a clear
      message — no dropdown is ever required to submit.
- [ ] On submit, the raw text is persisted to the `Order` table with
      status `pending_parse` before the parse call happens.
- [ ] After persistence, the backend calls the parsing service (see
      order-parsing skill) and updates the order to `parsed` or
      `needs_review`.
- [ ] The customer sees a confirmation message after submitting,
      regardless of how the parse turns out — they should never see or
      need to care about parsing status; that's Dad's concern, not
      theirs.
- [ ] If the backend is unreachable or the parse call fails outright,
      the raw text is still saved (status reflects the failure, e.g.
      `pending_parse` remains, or a distinct `parse_failed` status —
      pick one and note it here once decided) and the customer still
      sees a confirmation, not an error that implies their order wasn't
      received.

## Out of scope

- Admin dashboard display of these orders (separate spec).
- Editing/correcting a submitted order as the customer (not planned;
  corrections happen on the admin side).
- Real-time order status for the customer (e.g. "your order was
  parsed") — out of scope for v1.

## Open questions

- ~~Exact status value for "parse call failed outright" vs. "parse call
  succeeded but low confidence"~~ — **Resolved (2026-06-22):** keep the
  three statuses already in the AGENTS.md data model — no `parse_failed`.
  - A parse **call** that fails outright (API down/error) leaves the order
    at `pending_parse` so it can simply be retried later; the raw text is
    saved and the customer still sees a confirmation.
  - A parse that **succeeds but is low confidence** (or has unmatched text
    / an item not on the menu) → `needs_review`.
  Rationale: distinct failure modes, but they already map cleanly onto the
  existing statuses (retry-able vs. needs-a-human), so no new enum value is
  warranted. Keeps the model lean per this workflow's philosophy.
