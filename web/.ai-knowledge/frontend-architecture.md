# Frontend Architecture

## Layout

```
frontend/
  app/
    order/        public order form (customer-facing)
    admin/         admin dashboard (Dad-facing)
  components/
  lib/
```

## Key screens (current)

- `/order` — free-text order submission form. Client Component (needs
  interactivity for the textarea + submit state). Shows a confirmation
  state after submit, not a redirect — customer should see their order
  was received without losing context.
- `/admin` — order list. Server Component shell, with a Client Component
  for any interactive filtering/sorting. Each order row expands to show
  raw text + structured data side by side.
- `/admin/[orderId]` or an inline expand (TBD per spec) — correction UI
  for fixing a wrong parse.

## Conventions

- Server Components by default. Client Components only where
  interactivity is required (the order textarea, admin filtering,
  inline correction editing).
- No `any`. Co-locate component-specific types with the component file.
- `needs_review` orders must be visually distinct in any list view —
  not a small badge. This is a recurring requirement, not a one-off.

## Update this file when a new top-level route or major component
pattern is added.
