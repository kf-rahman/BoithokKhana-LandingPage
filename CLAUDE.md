# CLAUDE.md

## CRITICAL: Follow these personality guidelines strictly before responding

1. Exercise Quiet Confidence: trust your abilities without needing to
   prove them. State what you know simply. Acknowledge uncertainty
   directly rather than hedging everything.
2. This is a family business, not an enterprise client. Don't propose
   enterprise-scale solutions (microservices, k8s, multi-region) for a
   single-family catering operation. Default to the simplest thing that
   is genuinely production-correct.
3. The primary end user of the admin side (Dad) is not a developer.
   Every UI decision should be evaluated against "would Dad understand
   this without an explanation."
4. When uncertain about a product decision (not a technical one), stop
   and ask rather than guessing. Technical decisions (which library,
   how to structure a function) are yours to make.

## Further reading

- Foundation document that shapes this project as a product: @.ai/project-brief.md
- Backend architecture: @api/.ai-knowledge/backend-architecture.md
- Frontend architecture: @web/.ai-knowledge/frontend-architecture.md
- Backend tech stack: @api/.ai-knowledge/backend-tech-stack.md
- Frontend tech stack: @web/.ai-knowledge/frontend-tech-stack.md
- Engineering instructions: @.ai/engineering.md
- Order parsing domain contract: @.ai/order-parsing.md

## Memory

Follow the memory instructions in @.ai/memory.md

## Workflows (Tools)

- Code review workflow for backend: @api/.ai-knowledge/backend-code-review-workflow.md
  - Absolutely follow this file always when the user provides a git diff
    or other context and asks for a review
- Code review workflow for frontend: @web/.ai-knowledge/frontend-code-review-workflow.md
- Task preparation workflow: @.ai/tools/task-preparation-workflow.md
  - Don't follow this workflow unless the user specifies it
- Task execution workflow: @.ai/tools/implementation-workflow.md
  - This workflow runs after task-preparation-workflow.md, so at this
    stage a specific knowledge/ folder already exists with trd.md and
    implementation-strategy.md
  - Absolutely follow this file always when the user asks about it
