# Story: Auto-structure a free-text order

**As a** Dad (admin)
**I want to** turn each customer's free-text order into a structured list of menu
items and quantities, checked against this week's menu
**So that** I stop retyping every WhatsApp message into Excel — while still being
warned about anything the computer wasn't sure of, before I cook it

## Acceptance criteria

- [ ] An admin can trigger parsing of a submitted order; its raw text becomes
      structured line items (item, quantity, notes).
- [ ] Each line item is matched against the **published** menu — a match links to
      that menu item; an unmatched item is kept but left unlinked.
- [ ] An order with everything matched and high/medium confidence → `parsed`.
- [ ] An order with any unmatched item, leftover unmatched text, or low
      confidence → `needs_review` (never silently accepted).
- [ ] The computer never invents an item that isn't on the menu.
- [ ] The customer's raw text is unchanged after parsing (and after a re-parse).
- [ ] If parsing fails (API error/invalid output), the order is still safe: raw
      text intact, marked `needs_review`, nothing invented.
- [ ] The order records which week's menu it was parsed against.

## Edge cases this story must handle

- Item not on this week's menu → kept as an unlinked line item; order
  `needs_review`.
- No menu published → `needs_review` (can't validate against anything).
- Parser/API failure or schema-invalid output → `needs_review`; raw text never
  lost; no invented items.
- Re-parsing replaces the structured items but never the raw text.

## Out of scope for this story

- The admin dashboard to review/correct parses (next feature).
- Auto-parsing on submission (kept as an explicit admin trigger for v1).
- Pricing / totals.

## Open questions

- Admin auth — resolved: shared PIN (v1).
