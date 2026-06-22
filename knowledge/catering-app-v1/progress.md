# Progress — Catering Order System v1 (Workflow 2)

## Backend  ✅ done — 12/12 tests pass; alembic upgrade head verified
- [x] Project files: requirements.txt, app package, config, async db engine/session
- [x] Models: Order, MenuWeek (Uuid, JSON, UTC timestamps)
- [x] Schemas: Pydantic v2 (OrderCreate/Read, MenuWeekCreate/Read, correction)
- [x] Alembic: env (sync) + initial migration (0001_initial)
- [x] Service: order create + list (persist raw + pending_parse first)
- [x] Service: menus (create/publish, get_current)
- [x] Service: order_parsing (Claude via to_thread, 2 confidences, never-invent, matching)
- [x] Service: correction (preserve raw, set corrected_at/note) + flags
- [x] Service: CSV export
- [x] Routers: public (orders, menus) + admin (PIN-gated)
- [x] main.py: app, CORS, router wiring, create-all fallback for local
- [x] Tests: happy path, raw-preserved-on-failure, never-invent→needs_review,
      item-not-on-menu→needs_review, low-delivery-confidence-doesn't-block,
      correction-preserves-raw, totals, csv, parse-pending guard. All green.

## Frontend  ✅ done — type-check clean; routes 200 on a live run
- [x] Scaffold Next.js + brand CSS/layout/nav reused from the shared base
- [x] lib/api.ts; components (Header/Footer/HealthStatus); root layout
- [x] app/order/page.tsx (form + this week's menu + confirmation/error/loading)
- [x] app/admin/page.tsx + OrderCard + MenuPublish + types (PIN gate,
      raw|structured side by side, needs_review distinct banner, inline
      correction editor with menu re-matching, delivery-confirm prompt,
      parse / parse-all with spinners, menu publish, CSV export)
- [x] type-check clean

## Wrap-up  ✅
- [x] Self code-review vs api/web .ai-knowledge checklists (notes below)
- [x] Deploy parity: backend/Dockerfile, .dockerignore, docker-compose.yml,
      .env.example, README-APP.md
- [x] Session log: .ai/sessions/2026-06-22-workflow2-full-build.md
- [x] .ai-knowledge docs updated to match the build (model fields, async
      stack, frontend test-runner decision)
- [x] End-to-end verified incl. a real Claude parse (status parsed; item
      conf high / delivery conf low did NOT gate review; total $34.00)
- [ ] Commit + push workflow2  ← final step

## Review notes / known follow-ups
- OrderCard.tsx (~330 lines) is over the ~200-line guideline — cohesive but
  the correction editor could be extracted later.
- No frontend component test runner yet (Vitest+RTL) — deliberately deferred;
  type-check is the current guard. Backend has 12 tests.
- No order-delete endpoint/UI (not a stated requirement; correction is the
  intended path and avoids losing an order).
