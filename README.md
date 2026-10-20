# Boithok Khana

The website for Boithok Khana — a Bengali restaurant and catering kitchen at
7 Simcoe St South, Oshawa, ON.

It is one file: **`index.html`**. Self-contained CSS and JS, no build step,
no backend, no database. Open it in a browser and that's the site.

```
index.html                      the entire site
favicon.svg                     tab icon
Dockerfile                      nginx image Render runs
docker/nginx.conf.template      ...and its config
render.yaml                     the Render service
scripts/keep-warm.sh            uptime ping (free Render services sleep)
.github/workflows/keep-warm.yml ...on a cron
.claude/agents/                 the agents that maintain the site
```

## The page

A single page that swaps sections with `showPage(id)`: `home`, `gallery`,
`menu` (the standing shop menu, in time-of-day tabs), `weekly` (the rotating
Weekly Meal Menu), `contact`.

Customers order on WhatsApp (+1 437 993-1626), Facebook Messenger, or email
(bkfoodformulaz@gmail.com).

## Working on it

```bash
python3 -m http.server 8080      # http://localhost:8080
```

Push to `merge-wf1-wf3` and Render redeploys. See `DEPLOY.md`.

Three agents maintain it — `menu-updater`, `weekly-menu-updater`,
`site-logistics`. See `CLAUDE.md`.

## History

This repo previously held an online order form: a Next.js frontend, a FastAPI
backend, Postgres, and LLM-based parsing of free-text orders, built with an
orchestrated multi-agent workflow (`blogpost.md` tells that story). It was
removed in October 2026 — the API had stopped answering and orders were
coming in over WhatsApp regardless. All of it is still in git history and on
the `workflow-1` / `workflow2` / `workflow3` branches.
