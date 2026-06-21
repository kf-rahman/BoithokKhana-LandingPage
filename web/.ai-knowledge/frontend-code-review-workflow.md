# Frontend Code Review Workflow

## Review checklist

1. **Server vs Client Components** — is anything marked `"use client"`
   that doesn't actually need interactivity? Is anything that needs
   interactivity missing the directive?
2. **TypeScript** — any `any` slipped in? Are component-specific types
   co-located rather than dumped in a shared file?
3. **Component size** — is any single component pushing past ~200
   lines? Should something be extracted?
4. **UI states** — does this implement loading, empty, error, AND any
   domain-specific states (e.g. `needs_review`) the spec called for? Or
   only the happy path?
5. **`needs_review` visibility** — if this touches an order list view,
   is the flagged state visually obvious, not a small badge easy to
   miss?
6. **Plain-language test** — could Dad use this without an explanation?
   If a button or label needs a tooltip to be understood, the label is
   probably wrong.
7. **Tests** — does new interactive behavior have a test?

## Output

Short list, severity-ordered. Don't rubber-stamp.
