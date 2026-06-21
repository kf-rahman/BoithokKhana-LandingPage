---
name: build-feature
description: Orchestrates the full factory pipeline (researcher -> story-writer -> spec-writer -> backend-builder -> frontend-builder -> test-verifier -> implementation-validator) for any non-trivial feature request on the catering order system. Use this whenever the user asks for a new feature, a significant change to existing behavior, or anything touching order parsing or the admin dashboard. Do not use for trivial one-line fixes or pure styling tweaks - those can be handled directly in the main session.
---

# Build Feature — Factory Orchestration

You are the lead engineer (the main session). This skill defines how you
delegate a feature request across the seven specialist subagents instead
of doing everything yourself in one undifferentiated pass.

## When to use this skill

Use it for: new customer-facing features, new admin-dashboard features,
anything touching the order data model, anything touching the parsing
service, and any change where getting it wrong has a real-world
consequence (wrong food prepped, missed order, lost customer data).

Do NOT use it for: typo fixes, pure CSS/styling tweaks with no behavior
change, dependency bumps, or anything explicitly described as a quick
one-off. Use judgment — when in doubt, use the full pipeline. The cost of
over-using it is some extra time; the cost of under-using it on this
project is a real order getting mishandled.

## The pipeline

Run these steps **in order**. Do not skip steps. Do not let a later
subagent start before an earlier one's output exists on disk — each step
reads files the previous step wrote.

### 1. Delegate to `codebase-researcher`

Give it the raw feature request. Wait for its summary of what exists,
what's missing, and open questions.

### 2. Delegate to `story-writer`

Give it the feature request plus the researcher's summary. It writes
`docs/stories/<slug>.md`. Read the resulting story yourself before
continuing — if it split one request into multiple stories, treat each
as a separate pass through steps 3–7, or confirm with the user which to
prioritize first.

### 3. Delegate to `spec-writer`

Give it the story file path. It writes `docs/specs/<slug>.md`. Read it.

**Checkpoint:** if the spec has non-trivial Open Questions (especially
anything about admin auth, or any product decision rather than technical
one), surface these to the user now rather than letting builders guess.
Pause and ask, unless the user has already told you how to resolve them.

### 4. Delegate to `backend-builder`

Give it the spec file path. Wait for its summary of what was implemented
and whether existing tests still pass.

### 5. Delegate to `frontend-builder`

Give it the spec file path. This can happen after backend-builder, or
you can note that the API contract is now implemented and let it
proceed. Wait for its summary.

### 6. Delegate to `test-verifier`

Give it the story and spec file paths. It writes acceptance tests and
reports which criteria are covered and the full suite's pass/fail status.

### 7. Delegate to `implementation-validator`

Give it the story, spec, and test-verifier's report. It returns a
verdict: READY FOR HUMAN REVIEW or NOT READY.

## If the verdict is NOT READY

Read exactly what was flagged. Route the specific gap back to the
correct subagent (usually backend-builder or frontend-builder) rather
than re-running the entire pipeline. Then re-run implementation-validator
only, not the whole chain, once the gap is addressed.

## When everything passes

Summarize for the human, in plain language, what was built and what
they should look at. Point to the PR checklist at `docs/pr-checklist.md`
— a human (the user, or eventually Dad via the user) should review
against that checklist before merge, even though implementation-validator
already passed it.

## Context discipline

Each subagent works in its own context window and returns only a
summary — that's the entire point of this pipeline. Don't paste full
file contents between steps in your own responses to the user; reference
file paths instead (`docs/specs/order-parsing-v1.md`) so the user can
open them directly if they want detail.
