# Spec: Orders overview table

## Goal

A birds-eye table of every order on the admin dashboard so Dad can scan the
whole week at once, above the detailed per-order cards.

## Constraints

- Read-only; the same data as the CSV. `needs_review` rows visually distinct.

## Acceptance criteria

- [x] `/admin` shows a table with one row per order: short id, customer,
      status, items summary, total, delivery date, email-sent, delivered.
- [x] `needs_review` rows are visually highlighted.
- [x] A footer row shows the week's revenue total.

## Out of scope

- Sorting / filtering controls (v1 is a static overview).

## Open questions

- None.
