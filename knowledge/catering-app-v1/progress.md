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

## Frontend
- [ ] Scaffold Next.js (package.json, tsconfig, tailwind, next config)
- [ ] globals.css: brand vars + classes from index.html; Font Awesome CDN
- [ ] lib/api.ts; components/Header.tsx; root layout
- [ ] app/order/page.tsx (form + menu + confirmation/error/loading)
- [ ] app/admin/page.tsx (PIN, raw|structured, needs_review distinct,
      correction editor, delivery-confirm prompt, menu publish, CSV)
- [ ] type-check clean

## Wrap-up
- [ ] Backend + frontend code-review workflow pass
- [ ] Deploy parity: Dockerfile, docker-compose, .env.example, README
- [ ] Session log in .ai/sessions/ (order-parsing + admin touched)
- [ ] Commit + push workflow2
