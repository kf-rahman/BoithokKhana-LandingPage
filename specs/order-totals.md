# Spec: Order totals

## Goal

Show the money value of each order (and the week's revenue) so Dad can see
what a day/week is worth at a glance.

## Constraints

- Money is integer cents, never float (AGENTS.md). Totals derive only from
  matched menu items (which carry `unit_price_cents`).

## Acceptance criteria

- [x] Each order exposes `total_cents` = sum over structured items of
      `quantity × unit_price_cents` (matched items only).
- [x] The total shows on the order in the admin dashboard and in the CSV.
- [x] Unmatched items (no price) contribute 0, never an error.

## Out of scope

- Taxes, discounts, delivery fees.

## Open questions

- None.
