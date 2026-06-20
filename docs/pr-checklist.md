# PR Review Checklist

Every AI-generated PR must be checked against this list before merge —
including PRs that only touch tests or docs. This exists because
implementation-validator runs automatically, but a human (you, and
eventually whoever else helps maintain this) is the final gate.

## Always check

- [ ] `implementation-validator`'s verdict was READY, and you've read
      its acceptance-criteria table yourself (not just trusted the verdict).
- [ ] The diff actually matches the spec in `docs/specs/` — skim it,
      don't just trust the subagent summaries.
- [ ] No `.env` files, API keys, or database credentials in the diff.
- [ ] Tests were added or updated for any new behavior, and they pass.

## If this PR touches order parsing

- [ ] Raw customer text is persisted before the parse attempt, not after.
- [ ] Raw text is never overwritten by a structured correction.
- [ ] A genuinely ambiguous test case results in `needs_review`, not a
      guessed value — confirm this was actually tested, not just claimed.
- [ ] The current week's menu is passed as context to the parsing call.

## If this PR touches the admin dashboard

- [ ] Raw text and structured data are both visible for every order.
- [ ] `needs_review` orders are visually obvious, not just a small badge
      easy to miss.
- [ ] Error and empty states were actually implemented, not just listed
      in the spec.
- [ ] You (or someone non-technical, ideally) could use this without an
      explanation. If you have to explain a button's purpose, the label
      is wrong.

## If this PR touches money or pricing

- [ ] Integer cents or `Decimal` used — search the diff for `float` near
      price/amount/cost/total fields.

## If this PR touches dates or delivery scheduling

- [ ] Timezone handling is explicit — UTC stored, local time displayed.

## Before merging

- [ ] Pulled the branch locally and actually clicked through the feature
      once, end to end, as a customer would and/or as Dad would.
- [ ] CSV export (if touched) was opened in an actual spreadsheet app to
      confirm it's usable, not just schema-valid.
