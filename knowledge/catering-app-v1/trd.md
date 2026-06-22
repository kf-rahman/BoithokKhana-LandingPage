# TRD — Catering Order System v1 (Workflow 2, full build)

## Original requirements
Build the complete Family Catering Order System on the `workflow2`
branch using the Softcery-style workflow (autonomous full build, chosen
by the user). Same product as @/.ai/project-brief.md; this is an
independent implementation following this repo's prescribed architecture
(@api/.ai-knowledge/backend-architecture.md,
@web/.ai-knowledge/frontend-architecture.md), not a copy of Workflow 1.

## Acceptance criteria (testable)
1. A customer can submit a free-text order with name, contact (phone),
   optional email. The Order row is persisted with `raw_text` and status
   `pending_parse` **before** any parse call — a parse failure never
   loses the order. (@.ai/order-parsing.md flow step 2)
2. The parser returns the schema in @.ai/order-parsing.md: `items[]`,
   `delivery_date`, `delivery_notes`, **separate** `item_confidence` and
   `delivery_confidence`, `unmatched_text`. Output is schema-validated
   server-side.
3. Never-invent: an uncertain item, a non-empty `unmatched_text`, or an
   item name not on the active week's menu ⇒ status `needs_review`. The
   model's confidence claim is never trusted without shape validation.
4. `delivery_confidence: low` does NOT force `needs_review`; it surfaces
   a "confirm delivery date" prompt in the admin view.
5. Admin (PIN-gated) sees every order's raw text and structured parse
   side by side regardless of status; `needs_review` is visually
   distinct (not a small badge).
6. Dad can correct a parse (edit structured items) without altering
   `raw_text`; correction sets `corrected_at` + `correction_note`.
7. Weekly menu (`MenuWeek`) drives item matching and pricing. Totals are
   computed in integer cents — never float.
8. CSV export of orders opens cleanly in a spreadsheet.
9. Times stored UTC; delivery dates handled explicitly.
10. Backend tests cover: happy path, raw-text-preserved-on-parse-failure,
    never-invent ⇒ needs_review, correction preserves raw text, totals.

## Dependencies / touches
- Fresh `backend/` (FastAPI, async SQLAlchemy) and `frontend/` (Next.js).
- Reuses the live `index.html` brand CSS (per the styling decision).
- Anthropic key from `backend/.env` (gitignored).
- High-stakes areas touched: order-parsing AND admin dashboard ⇒ session
  log required per @.ai/memory.md.

## Resolved decisions
- **Admin auth**: shared PIN, changeable via env (`ADMIN_PIN`). The user
  resolved this earlier for this product; not re-opening it. (Satisfies
  the "don't silently assume" non-negotiable: it's an explicit decision,
  not an assumption.)
- **DB**: async SQLAlchemy; `sqlite+aiosqlite` locally (runs without
  Docker, per the user's deferral), `postgresql+asyncpg` for deploy.
</content>
</invoke>
