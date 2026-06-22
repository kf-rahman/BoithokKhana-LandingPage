# Spec: Fulfillment tracking (email sent / delivered)

## Goal

Let Dad mark, per order, whether the confirmation has been sent and whether
it's been delivered — the operational checkboxes he used to keep in Excel.

## Constraints

- Extends the AGENTS.md `Order` model with two booleans
  (`confirmation_email_sent`, `delivered`); update AGENTS.md + add a
  migration. Raw text and the parse are untouched.

## Acceptance criteria

- [x] `Order` gains `confirmation_email_sent: bool` and `delivered: bool`,
      default false, in the model and a migration.
- [x] A PIN-gated PATCH can toggle either flag without affecting the parse,
      status, or raw text.
- [x] The admin UI shows each flag and lets Dad toggle it; state persists.
- [x] Both flags appear in the CSV.

## Out of scope

- Actually sending email (manual flag only, consistent with the project).

## Open questions

- None.
