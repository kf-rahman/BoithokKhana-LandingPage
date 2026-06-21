# Softcery-Style Setup — Family Catering Order System

This is the "dual-tool, persistent memory" agentic setup, wired to your
project. Unlike the Software Factory (Workflow 1), there are no
subagents here — instead, the system relies on a modular `CLAUDE.md` /
`.cursor/rules/*.mdc` context layer, a `.ai/memory.md` protocol for
session continuity, and a two-phase plan-then-execute workflow.

## What's in this folder

```
CLAUDE.md                              — thin root file, points everywhere else
.ai/
  project-brief.md                     — the product-level "why"
  engineering.md                       — cross-cutting standards + non-negotiables
  memory.md                            — session-logging protocol
  order-parsing.md                     — domain contract for the hard part
  tools/
    task-preparation-workflow.md       — phase 1: plan
    implementation-workflow.md         — phase 2: execute
  sessions/                            — dated session logs accumulate here
.cursor/rules/
  core.mdc                             — always-applied context (Cursor)
  backend.mdc                          — scoped to backend/**/*.py
  frontend.mdc                         — scoped to frontend/**/*.tsx,ts
api/.ai-knowledge/
  backend-architecture.md
  backend-tech-stack.md
  backend-code-review-workflow.md
web/.ai-knowledge/
  frontend-architecture.md
  frontend-tech-stack.md
  frontend-code-review-workflow.md
.claude/settings.json                  — a deterministic hook (not just a prompt rule)
knowledge/                             — task-prep creates a folder per feature here
```

## How this differs from the Software Factory (Workflow 1)

No subagents. One continuous session, guided by:
- A **thin CLAUDE.md** that's mostly pointers (`@file` references) —
  keeps the always-loaded context small.
- A **memory protocol** (`.ai/memory.md`) so a new session can pick up
  where the last one left off, instead of re-deriving context from the
  codebase every time.
- A **two-phase workflow**: task-preparation (plan, write
  `implementation-strategy.md`) then implementation (execute against
  that strategy, checklist-style via `progress.md`). This is invoked
  explicitly, not automatically — the workflow files say "don't follow
  this unless the user specifies it."
- **Both Claude Code and Cursor are supported** — the same
  `.ai/*.md` files are referenced from both `CLAUDE.md` (via `@`) and
  the Cursor `.mdc` rules (via relative `@../../`).

## How to use it day to day

For a new feature, two-step it explicitly:

```
Prepare the task: customer order submission with free-text parsing
```

This creates `knowledge/order-submission/trd.md` and
`implementation-strategy.md`. Review the strategy file yourself —
this is the checkpoint where you catch a wrong approach before any code
is written.

Then:

```
Implement the order-submission task
```

This works through `progress.md` checklist-style, possibly across
multiple sessions — that's the point of `progress.md` existing as a
file rather than living only in chat history.

For a code review:

```
Review this diff against our backend code review workflow
```

This pulls in `api/.ai-knowledge/backend-code-review-workflow.md`
automatically per the CLAUDE.md routing.

## Install steps

1. Copy this entire folder structure into your repo root.
2. Create `backend/` and `frontend/` matching the structure referenced
   in `.ai/engineering.md` if they don't exist yet.
3. If using Cursor: the `.cursor/rules/*.mdc` files are picked up
   automatically — no extra config needed, but confirm you're not also
   running a legacy `.cursorrules` file, which is deprecated and
   silently ignored in Agent mode.
4. If using Claude Code: `CLAUDE.md` and `.claude/settings.json` load
   automatically from the repo root.

## A note on memory accumulation

`.ai/sessions/` will grow over time. Per `.ai/memory.md`, only sessions
with non-obvious decisions or changes to the high-stakes areas
(order-parsing, admin dashboard) get logged — this is meant to stay a
curated decision record, not a transcript of every session. If it starts
feeling noisy, that's a sign the logging discipline has slipped — prune
it back to what's actually useful for a future session to read.
