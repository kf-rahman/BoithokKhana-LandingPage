# Engineering Instructions

## Stack

- Frontend: Next.js (App Router), TypeScript, Tailwind CSS
- Backend: FastAPI (Python)
- Database: PostgreSQL via SQLAlchemy + Alembic
- Order parsing: Claude API, called server-side
- Local dev: localhost only for now (frontend :3000, backend :8000,
  Postgres via Docker Compose). Do not add deployment config (Vercel,
  Railway, etc.) unless explicitly asked.

## Non-negotiables

These apply regardless of which feature is being worked on:

1. **Raw order text is permanent.** Never overwritten, never deleted.
   Stored alongside whatever structured data is derived from it.
2. **Never invent order data.** If the parser is uncertain about an
   item, quantity, or modifier, it must flag for manual review rather
   than guess. This is enforced in @.ai/order-parsing.md.
3. **Money is integer cents or Decimal.** Never float.
4. **Timezones are explicit.** Store UTC, display local time. Don't
   leave timezone handling implicit anywhere a delivery date is
   involved.
5. **Admin auth method is not assumed.** It is a deliberately
   unresolved decision — surface it the first time a task touches
   `/admin` routes or auth, don't silently pick shared-password or
   real-login.

## Coding standards

**Backend (FastAPI):**
- Type-hint everything.
- Pydantic schemas for all request/response bodies.
- No bare `except:`.
- Business logic lives in `services/`, not in route handlers.

**Frontend (Next.js):**
- Server Components by default; Client Components only where
  interactivity requires it (forms, the order textarea, dashboard
  filtering).
- No `any` in TypeScript.
- Keep components under ~200 lines; extract subcomponents/hooks instead
  of letting one file grow.

## When something goes wrong

If the agent makes a mistake in this codebase — a bug, a wrong
assumption, a performance issue — the fix is not just to patch the code.
Update the relevant `.ai-knowledge/` file (backend-architecture.md,
frontend-architecture.md, or this file) with a short note so the same
mistake doesn't happen again next session. Every mistake becomes a
prevention rule; every successful pattern becomes a reusable note in
`.ai/tools/`.
