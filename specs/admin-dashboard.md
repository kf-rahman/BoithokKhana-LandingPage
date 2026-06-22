# Spec: Admin dashboard (Dad-facing)

## Goal

One screen for Dad: see every order with the customer's raw text next to
the structured parse, fix a wrong parse, publish the weekly menu, and
export orders as CSV for prep/shopping. Replaces the Excel half of the old
WhatsApp+Excel workflow.

## Constraints

- AGENTS.md non-negotiables: raw text is never overwritten (a correction
  sets `corrected_at` + `correction_note` only); the parser never invents;
  money is integer cents; times stored UTC.
- **Admin auth (non-negotiable #3) — RESOLVED:** shared PIN sent as the
  `X-Admin-Pin` header, value from the `ADMIN_PIN` env var (default `1234`,
  **must be changed before real use**). This matches the product owner's
  earlier explicit choice ("the security thing is ok for now, just make
  sure I can change the password"). It is not a real login — revisit if
  multiple staff or stronger auth become necessary.
- The order-parsing skill governs parse / `needs_review` behavior and the
  raw|structured display.

## Acceptance criteria

- [x] Every admin endpoint requires a correct PIN; missing/wrong → 401.
- [x] Dad can load all orders and see, per order, raw text and the
      structured parse side by side, regardless of status.
- [x] `needs_review` orders are visually distinct — not a small badge.
- [x] Dad can correct a parse (edit items/quantities/notes) and save;
      `raw_text` is unchanged, `corrected_at` + `correction_note` are set,
      and the order leaves `needs_review`.
- [x] When `delivery_confidence` is low and no date is set, a "confirm
      delivery date" prompt shows (doesn't block the rest of the order).
- [x] Dad can (re)parse pending orders — e.g. ones whose parse call failed
      — individually and in bulk.
- [x] Dad can publish the current week's menu (dish names + prices).
- [x] Dad can export all orders to a CSV that opens cleanly in a sheet.

## Out of scope

- Delivered / confirmation-email tracking flags — not in the AGENTS.md data
  model; adding them is a deliberate model change + migration, not this spec.
- Deleting orders (correction is the path; deleting risks losing an order).
- Real per-user login (see the auth note above).

## Open questions

- None blocking — auth resolved above.
