# Story: Submit an order in plain text

**As a** customer
**I want to** place my order by typing it in my own words (like a WhatsApp
message), giving just my name and a phone number
**So that** ordering feels as easy as texting, and my order is never lost even
if something goes wrong on the business's side afterward

## Acceptance criteria

- [ ] A customer can submit an order providing only: their name, a phone
      number, and a single free-text order — no item dropdowns required.
- [ ] On submission the order is saved immediately, with the customer's order
      text stored exactly as typed (no trimming, normalizing, or reformatting
      of the order text).
- [ ] A newly submitted order is persisted with a status meaning "not parsed
      yet" (`pending_parse`).
- [ ] The submission response confirms receipt and includes the order's id and
      status.
- [ ] Submitting with an empty / whitespace-only order (or missing name/phone)
      is rejected with a validation error, and no order row is created.
- [ ] The raw order text lives in its own field that the (future) parser will
      never overwrite.

## Edge cases this story must handle

- Empty or whitespace-only order text: rejected with a validation error; no row
  saved.
- Unusual free text (emojis, line breaks, several items in one message):
  accepted and stored verbatim.
- Parsing not available yet (it's a later feature): the order is still saved
  with `pending_parse` — saving raw text never depends on a successful parse.
  This is the failure mode that matters most: a parser/API outage must not lose
  a customer's order.

## Out of scope for this story

- LLM parsing of the free text into structured items (next feature).
- Any Dad/admin-facing read, list, correction, or CSV export of orders
  (admin-dashboard feature — which also resolves the admin-auth question).
- Wiring the existing `/order` form (frontend) to this endpoint — backend-only
  this slice.
- Pricing / money handling (arrives with the menu feature).

## Open questions

- Persistence engine while Docker/Postgres is deferred — resolved as a
  documented call: local SQLite now, kept cleanly Postgres-swappable (see spec).
- Admin authentication — not engaged by this story (there are no read endpoints
  here); remains open for the admin-dashboard feature.
