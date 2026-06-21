# Project Brief — Family Catering Order System

## The problem

A small family-run weekly meal/catering business currently runs entirely
on manual labor for order intake:

1. Dad posts this week's menu on Facebook.
2. A customer reads it and texts Dad on WhatsApp with their order, in
   free-form natural language — items mix and match every week, so a
   fixed menu/dropdown doesn't represent what people actually order
   ("2 chicken biryani no spice, 1 veg thali, extra rice, deliver friday
   evening").
3. Dad manually retypes every WhatsApp message into an Excel sheet.
4. The Excel sheet is what's actually used to plan prep and shopping.

This is slow, error-prone (manual retyping), and doesn't scale past the
current order volume.

## The product

A web app with two surfaces:

1. **Customer order page** — public, no login. A free-text box where a
   customer types their order exactly like they'd text it on WhatsApp.
   No dropdowns for items, because the menu changes weekly and items
   combine in ways a fixed form can't anticipate.

2. **Admin dashboard** — Dad-facing. Shows every order in two forms
   side by side: the raw text the customer typed, and a structured
   parse of it (items, quantities, modifiers, delivery info). Supports
   CSV export for prep/shopping planning. Lets Dad correct a wrong
   parse without losing the original text.

## Who this is for

- **Customers**: ordering quickly, often on a phone, expect something
  close to the WhatsApp experience they're used to.
- **Dad**: not a developer, runs this business operationally every
  week, needs to trust the data enough to actually shop and cook from
  it. Will not tolerate a confusing interface and will not debug one.

## What "done" looks like

Genuinely production-usable, not a prototype. Specifically:
- Dad can fully replace WhatsApp + Excel with this for a real week of
  orders.
- A parsing failure or low-confidence parse never silently produces a
  wrong order — it's flagged, and the raw text is always there as the
  source of truth.
- CSV export opens cleanly in whatever spreadsheet app Dad already uses.

## What's explicitly out of scope for now

- Payments/billing.
- Multi-business / multi-tenant support — this is one family's business.
- Native mobile app — responsive web is enough.
- Automated SMS/WhatsApp integration — the web form replaces WhatsApp
  texting, it doesn't read WhatsApp messages.
