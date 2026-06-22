# Spec Template

Copy this into `specs/<feature-slug>.md` for every non-trivial feature.
This is the entire planning artifact — no separate story file, no
subagents, no orchestrator. The spec is the contract between you (team
leader) and the agent (super-domestique).

Keep it short. If it's getting long enough to need its own table of
contents, the feature is probably too big for one spec — split it.

```markdown
# Spec: <feature name>

## Goal

<One or two sentences. What does this let a customer or Dad actually
do, and why does it matter for replacing the WhatsApp+Excel process?>

## Constraints

<Anything non-negotiable from AGENTS.md that's especially relevant
here. Don't restate everything — just what's load-bearing for this
specific feature.>

## Acceptance criteria

- [ ] <specific, testable>
- [ ] <specific, testable>

## Out of scope

<What this spec deliberately does not cover, so the agent doesn't
scope-creep.>

## Open questions

<Anything that's a decision for you, not the agent, to make before or
during implementation.>
```

## How to use this

1. Write the spec yourself (or ask the agent to draft one from a rough
   description, then edit it — either is fine, you review either way).
2. Hand it to the agent along with the relevant skill, e.g.:
   "Implement specs/order-submission.md. Load the order-parsing skill
   first."
3. Review the output against the acceptance criteria yourself. There's
   no separate validator subagent — you are the validator.
4. If you hit a recurring mistake during review, add it to AGENTS.md
   directly so it doesn't happen again next time.
