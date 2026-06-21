# Task Preparation Workflow

Don't follow this workflow unless the user specifies it (e.g. "prepare
the task for X" or invokes `/task-preparation`).

When given a new feature, do the following:

1. **Create a knowledge folder** for the task at `knowledge/<feature-slug>/`
   (e.g. `knowledge/order-submission/`).

2. **Add `trd.md`** (Task Requirement Document) to that folder, containing:
   - Original requirements (as given by the user, lightly cleaned up)
   - Acceptance criteria (specific, testable — not "works well")
   - Dependencies (what existing code/data model this touches or
     requires)
   - If this touches order parsing or the admin dashboard: explicitly
     reference @.ai/order-parsing.md and @.ai/engineering.md's
     non-negotiables, and confirm the acceptance criteria account for
     the `needs_review` path, not just the happy path.

3. **Review existing code** if relevant areas were specified by the
   user, or if `trd.md`'s dependencies section implies touching
   existing models/routes/components.

4. **Create `implementation-strategy.md`** in the same folder, with:
   - Database changes (model fields, migration needed)
   - API modifications (routes, request/response shapes)
   - UI components (what's new, what's changed)
   - Testing approach
   - Open questions — anything that's a product decision, not a
     technical one (flag admin-auth explicitly if this task touches it)

5. **Create `progress.md`** in the same folder for tracking — start it
   as an empty checklist derived from the implementation strategy.

6. **Await next instruction.** Do not start implementing yet — that's
   the implementation-workflow's job, and it should usually be a
   separate, deliberate next step so the strategy can be reviewed first.

## Why this two-phase split matters

By having the agent create `implementation-strategy.md` upfront, future
sessions don't need to re-analyze the entire codebase to figure out what
needs to be done — they read the strategy document and continue. This
is a real token/cost saving across a multi-session feature, not just
process theater.
