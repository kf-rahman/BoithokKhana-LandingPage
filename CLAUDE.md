# CLAUDE.md — Family Catering Order System

This file is always loaded into context. Keep it concise — detailed domain
knowledge belongs in `.claude/skills/`, not here.

## What this project is

A small CRM/order-management platform replacing a manual WhatsApp + Excel
workflow for a family-run weekly meal/catering business.

**The current (broken) process:**
1. Dad posts this week's menu on Facebook.
2. Customers text Dad on WhatsApp with their order, in free-form natural
   language ("2 chicken biryani no spice, 1 veg thali, deliver friday").
3. Dad manually retypes every order into an Excel sheet.
4. Excel is used to plan prep and shopping.

**What we're building instead:**
1. A public order page where a customer types their order as free text
   (no rigid dropdowns — the weekly menu changes and items mix and match).
2. An LLM-backed parser that converts that free text into structured order
   data (items, quantities, modifiers/notes, customer info, delivery info).
3. An admin dashboard (Dad-facing) that shows, per order: the **raw
   original text** the customer typed, and the **parsed/structured version**
   side by side. Dad can correct a misparse.
4. CSV export of structured orders for prep/shopping planning.

This must end up genuinely production-usable by a non-technical user (Dad).
Not a prototype. Error states, empty states, and "what does Dad do when the
parser gets it wrong" are first-class concerns, not edge cases.

## Tech stack

- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (via SQLAlchemy + Alembic migrations)
- **Order parsing:** Claude API (Anthropic), called server-side on order
  submission. See `.claude/skills/order-parsing/SKILL.md` for the prompt
  contract and output schema.
- **Local dev:** everything runs on localhost for now. Frontend on
  `:3000`, backend on `:8000`, Postgres via Docker Compose.
- **Deployment:** deploy config now lives in the repo (backend `Dockerfile`,
  root `docker-compose.yml`, `frontend/Dockerfile`) — see `DEPLOY.md`.
  Intended hosts: Vercel for the frontend; Railway/Render/Fly for the backend +
  Postgres (host not yet chosen).

## Repository structure

```
/frontend          Next.js app
  /app
    /order          public order form (customer-facing)
    /admin           admin dashboard (Dad-facing)
  /components
  /lib
/backend            FastAPI app
  /app
    /api             route handlers
    /models          SQLAlchemy models
    /schemas         Pydantic schemas
    /services        business logic (parsing, CSV export, etc.)
    /db               session/engine setup
  /alembic            migrations
  /tests
/.claude
  /agents             the 7 subagents
  /skills             reusable workflows + domain knowledge
  /hooks              pre-commit safety hook
/docs
  /specs              one file per feature, written by spec-writer
  /stories            one file per feature, written by story-writer
```

## Quick start commands

```
# backend
cd backend && uvicorn app.main:app --reload

# frontend
cd frontend && npm run dev

# db
docker compose up -d db
cd backend && alembic upgrade head

# tests
cd backend && pytest
cd frontend && npm test
```

## Coding standards

- **Backend:** type-hint everything, Pydantic schemas for all
  request/response bodies, no bare `except:`, business logic lives in
  `services/` not in route handlers.
- **Frontend:** Server Components by default; mark Client Components
  explicitly only when needed (forms, interactivity). No `any` in
  TypeScript. Co-locate component-specific types with the component.
- **Craftsmanship mindset:** every line of code should be intentional,
  readable, and maintainable. Write code you'd be comfortable explaining
  to a non-technical family member who depends on this working correctly
  every single week.
- **Money/quantities:** never use floats for prices. Use integer cents or
  `Decimal`.
- **Dates/times:** the business operates in a single timezone. Store as
  UTC, display in local time. Be explicit about this in any schema
  involving delivery dates.

## The orchestrated workflow (the "factory")

For any non-trivial feature request, the main session acts as lead
engineer and delegates to subagents in this order. Full detail in
`.claude/skills/build-feature/SKILL.md` — invoke it with
`/build-feature <description>` or just ask in plain language; the skill
description is written so Claude routes to it automatically for feature
work.

1. `codebase-researcher` — map what currently exists relevant to the ask.
2. `story-writer` — turn the idea into a user story with acceptance
   criteria, written from Dad's or the customer's point of view.
3. `spec-writer` — turn the story into a technical brief (data model,
   API contract, UI states, open questions).
4. `backend-builder` — implement API routes, services, DB models/migrations.
5. `frontend-builder` — implement components/pages against the spec's
   API contract.
6. `test-verifier` — write acceptance tests against the user story.
7. `implementation-validator` — compare the finished feature against the
   brief and story; flag any gap before it's considered done.

Do not skip the story/spec steps for anything touching the order-parsing
logic, the admin dashboard, or anything Dad will rely on operationally —
those are exactly the places where ambiguity becomes a real-world mistake
(wrong order prepared, missed delivery).

## Non-negotiables specific to this project

- The customer's **original raw text is never discarded or overwritten**.
  It is stored permanently alongside the structured parse. This is the
  fallback of last resort when parsing is wrong.
- The parser must never silently invent items that weren't in the
  customer's text. If it's not confident, it should flag the order for
  manual review rather than guess.
- Admin dashboard changes must be reviewed especially carefully — Dad is
  not a developer and will not debug a confusing UI. Favor obvious over
  clever.
- Admin auth is a **v1 shared PIN** (`X-Admin-Pin` header, value from the
  `ADMIN_PIN` env var). This was the product owner's decision — not a real
  login. Revisit if multiple staff or stronger auth become necessary.

## PR review checklist

See `docs/pr-checklist.md`. Every AI-generated PR must be checked against
it before merge — no exceptions, including PRs that only touch tests or
docs.
This branch (`merge-wf1-wf3`) is the integrated app: the workflow-1 base with
workflow-3's component-split admin dashboard ported onto it.