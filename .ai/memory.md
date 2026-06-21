# Working Memory

1. Document sessions in @.ai/sessions/.
2. Use the following file format: `{yyyy-mm-dd}-{title}.md`.
3. Use the following memory log file format: title, description, session
   log, session outcomes, lessons learned (if any).
4. Keep memories concise — only document what is worth documenting.
   Don't log a session where nothing of future relevance happened.
5. Document only when the user asks you to, OR when a session involved
   a non-obvious decision, a bug fix worth remembering, or a change to
   the order-parsing or admin-dashboard logic (these two areas are
   high-stakes per @.ai/engineering.md and deserve a record even if not
   explicitly requested).
6. Adjust @api/.ai-knowledge/backend-architecture.md,
   @web/.ai-knowledge/frontend-architecture.md, or
   @api/.ai-knowledge/backend-tech-stack.md if architecture changes or a
   new dependency is added.

## Example session log entry

```markdown
# 2026-06-20 — Order parsing confidence thresholds

## Description
Tuned the confidence thresholds for the order-parsing service after
testing against ~15 real WhatsApp messages from the existing order
history.

## Session log
- Started with confidence buckets at 0.9/0.7 (high/medium cutoffs).
- Found that delivery-date-only ambiguity ("this weekend" vs a specific
  date) was tanking confidence even when item parsing was solid.
- Split confidence scoring: item-parsing confidence and
  delivery-info confidence are now tracked separately. Only item
  confidence drives the needs_review flag.

## Session outcomes
- `services/order_parsing.py` now returns two confidence scores.
- Delivery-date ambiguity surfaces as a UI prompt ("confirm delivery
  date") rather than blocking the whole order into needs_review.

## Lessons learned
- Don't conflate "the model isn't sure what day this means" with "the
  model isn't sure what food this is." These have very different
  correct UI treatments and were originally one confidence score.
```
