# 2026-06-22 — Workflow 2 full build of the catering order system

## Description
Autonomous full build (user's choice) of the entire Family Catering Order
System on `workflow2`, using the Softcery workflow, as an independent
counterpart to the `workflow-1` software-factory build. Touches both
high-stakes areas (order parsing and the admin dashboard), so logged here
per @.ai/memory.md.

## Session log
- Planned via knowledge/catering-app-v1/ (trd, implementation-strategy,
  progress) rather than per-feature folders, since it was one continuous
  build.
- Backend: async SQLAlchemy 2.x, UUID PKs, Order + MenuWeek, structured
  parse stored as JSON, two confidence scores (item vs delivery),
  PIN-gated admin, Alembic initial migration. 12 pytest-asyncio tests.
- Parser: isolated synchronous Claude call wrapped in `asyncio.to_thread`
  (keeps the SDK call mockable and off the event loop). never-invent +
  needs_review derivation implemented and tested.
- Frontend: brand CSS reused from index.html; order page + admin
  dashboard built fresh against the softcery frontend architecture.
- Verified end to end against a real Claude parse: "2 chicken biryani no
  spice and 1 veg thali, deliver friday" => both items matched ($34.00),
  item_confidence high, delivery_confidence low, no date invented, status
  stayed `parsed` (low delivery confidence did not gate review).

## Session outcomes
- A runnable second version of the product on `workflow2`.
- Knowledge docs updated to match what was actually built (see below).

## Decisions / lessons learned
- **Async + SQLite locally.** Followed the prescribed async stack but
  defaulted `DATABASE_URL` to `sqlite+aiosqlite` so it runs with no Docker
  (user deferred Docker); `postgresql+asyncpg` for deploy. Alembic uses a
  sync driver derived from the same URL.
- **Model is richer than the architecture sketch.** Added
  customer_name/phone/email, confirmation_email_sent, delivered, and
  unmatched_text because those are real product requirements. Updated
  api/.ai-knowledge/backend-architecture.md to match — the sketch's single
  `customer_contact` would have lost required fields.
- **Low delivery confidence must not gate review.** Easy to conflate with
  item confidence; kept them fully separate and added a regression test.
- **Branding is shared, product logic is not.** Reused inert
  scaffolding/brand files from `workflow-1` (CSS, layout, nav, build
  config); built all backend + product UI fresh. Reusing branding is the
  documented styling decision and is not "porting the app."
