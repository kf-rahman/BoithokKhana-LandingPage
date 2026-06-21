# Backend Code Review Workflow

Absolutely follow this file always when the user provides a git diff or
other context and asks for a review.

## Review checklist

1. **Type hints** — everything type-hinted? Any implicit `Any` slipping
   through?
2. **Pydantic schemas** — every request/response body has one? No raw
   dict returns from route handlers?
3. **Business logic location** — is anything beyond simple
   orchestration sitting in a route handler instead of `services/`?
4. **Money fields** — search for `float` near price/amount/cost/total.
   Should be integer cents or `Decimal`.
5. **Timezones** — any `datetime.now()` without explicit UTC handling?
   Any delivery-date logic that doesn't account for timezone conversion
   at the display boundary?
6. **Order-parsing specific** (if touched): does raw text get persisted
   before the parse call, not after? Does a low-confidence or
   schema-invalid parse result in `needs_review`, not a silent guess?
   Cross-check against @.ai/order-parsing.md.
7. **Bare excepts** — any `except:` without a specific exception type?
8. **Tests** — does new logic have at least a happy-path test? Does
   anything order-parsing-related have a test for the ambiguous/failure
   case, not just the happy path?

## Output

Give findings as a short list, ordered by severity (correctness/data
integrity issues first, style issues last). Don't just say "looks good"
without walking through the checklist explicitly.
