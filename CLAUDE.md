# CLAUDE.md — Boithok Khana website

This file is always loaded into context. Keep it concise.

## What this project is

The website for **Boithok Khana**, a Bengali restaurant and catering business
at 7 Simcoe St South, Oshawa, ON. It is **one static page**: `index.html`.

There is no backend, no database, and no build step. `index.html` contains
its own CSS and JS and is served as-is. Customers order by WhatsApp
(+1 437 993-1626), Facebook Messenger, or email
(bkfoodformulaz@gmail.com) — the site's job is to show the menu and the
contact details, correctly.

> **History:** this repo used to also hold an online order form with a
> FastAPI backend, Postgres, and LLM order parsing. It was removed in October
> 2026 — the API had stopped answering and the family was taking orders on
> WhatsApp anyway. The whole thing is still in git history and on the
> `workflow-1` / `workflow2` / `workflow3` branches if it's ever wanted back.

## Page structure

`index.html` is a single page that shows one `<div class="page">` at a time
via `showPage(id)`:

| id        | What it is                                                  |
|-----------|-------------------------------------------------------------|
| `home`    | hero, services, highlights                                   |
| `gallery` | photos                                                       |
| `menu`    | the standing shop menu, in time-of-day tabs                  |
| `weekly`  | this week's Weekly Meal Menu (rotates; has markers, see below)|
| `contact` | contact details + subscribe/inquiry forms                    |

- The `#menu` tabs (`showMenu(id, btn)`) are `morning`, `luncheon`,
  `evening`, `dinner`, `breakfast`, `drinks`. A tab needs BOTH a
  `.menu-tab` button and a `.menu-content` div with the same id.
- The rotating part of `#weekly` sits between `<!-- WEEKLY-MENU-START -->`
  and `<!-- WEEKLY-MENU-END -->`.

## Deployment

Render, declared by `render.yaml`: a single Docker web service
(`boithok-web`) running nginx over `index.html`, serving
`www.boithokkhana.ca` and `boithokkhana.ca`. Render deploys from the
`merge-wf1-wf3` branch. Full detail in `DEPLOY.md`.

Free Render services sleep after 15 idle minutes, so
`.github/workflows/keep-warm.yml` pings the site every 10 minutes during an
11-hour daily window. **That window is sized against Render's 750 free
instance-hours per month, shared across the whole workspace — redo the
arithmetic in the workflow's comments before widening it.**

## The agents

Three agents maintain this site:

- `menu-updater` — the standing shop menu (`#menu`).
- `weekly-menu-updater` — this week's Weekly Meal Menu (`#weekly`).
- `site-logistics` — contact details, dead links, stale copy, deploy/uptime.

The other agents in `.claude/agents/` (`backend-builder`, `spec-writer`, …)
and the `build-feature` / `order-parsing` skills are **legacy from the order
app**. They describe code that no longer exists here. Don't route work to
them unless the order app is being revived.

## Rules

- **Never invent a dish, a price, hours, or a contact detail.** This is a
  real family business; a wrong price on the live menu costs them money, and
  a wrong phone number costs them an order. If a source is unreadable, leave
  the old value and say so.
- Keep the Bangla alongside the English in menu headings and dish names where
  the source has it — that's how customers recognise the dishes.
- Prices are written as printed, with two decimals and a `$`.
- Editing `index.html` *is* shipping, once pushed. Check the tags still
  balance before you commit.
