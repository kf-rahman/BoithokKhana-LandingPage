# Implementation Workflow

This workflow runs after task-preparation-workflow.md, so at this stage
there's already a `knowledge/<feature-slug>/` folder with `trd.md` and
`implementation-strategy.md`. Absolutely follow this file always when
the user asks about it (e.g. "implement the order-submission task" or
invokes `/implementation <feature-slug>`).

1. **Read** `knowledge/<feature-slug>/implementation-strategy.md`.

2. **Check or create** `knowledge/<feature-slug>/progress.md`.

3. **If new** (progress.md is empty or doesn't exist): break the
   strategy into a subtasks checklist in `progress.md`.

4. **If existing**: identify the next incomplete task in the checklist.

5. **Implement the next task.** Follow the standards in
   @.ai/engineering.md without exception — especially the
   non-negotiables (raw text preservation, no invented order data,
   money as integer/Decimal, explicit timezones, admin-auth not
   assumed).

6. **Update `progress.md`** — mark the task done, note anything
   discovered along the way that the next task should know about.

7. **Repeat** until the checklist in `progress.md` is complete.

8. **Once complete**, run the relevant code review workflow
   (@api/.ai-knowledge/backend-code-review-workflow.md and/or
   @web/.ai-knowledge/frontend-code-review-workflow.md depending on
   what was touched) before telling the user the feature is done.

9. **Log the session** per @.ai/memory.md if anything non-obvious
   happened, or if this task touched order-parsing or the admin
   dashboard (always log those, per the memory instructions).

## On deviation from the strategy

If implementing a task reveals the strategy was wrong or incomplete,
don't silently improvise — update `implementation-strategy.md` itself
with the correction and a one-line note on why, then continue. The
strategy document should stay accurate, not just the code.
