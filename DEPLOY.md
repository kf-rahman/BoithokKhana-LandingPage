# Deploying the Boithok Khana site

The site is one static page, `index.html`, served by nginx in a small Docker
image. There is no backend and no database.

> **What changed (October 2026):** this used to be three services — a Next.js
> frontend, a FastAPI backend, and a Postgres database, serving an online
> order form with LLM order parsing. The order app was removed; orders come
> in on WhatsApp and Messenger. The old blueprint and code are in git history
> and on the `workflow-1` / `workflow2` / `workflow3` branches.

## Looking at it locally

No toolchain needed — open `index.html` in a browser, or:

```bash
python3 -m http.server 8080      # then http://localhost:8080
```

To check the real production image (needs Docker running):

```bash
docker build -t bk-site .
docker run --rm -p 8080:10000 -e PORT=10000 bk-site
curl -s localhost:8080/health    # -> ok
```

## Production — Render

`render.yaml` declares one service:

| Service       | What it does                                              |
|---------------|-----------------------------------------------------------|
| `boithok-web` | nginx serving `index.html` on `www.boithokkhana.ca`        |

Render builds from the **`merge-wf1-wf3`** branch — push to it and Render
redeploys automatically. A failed build does **not** take the site down;
Render keeps serving the last good deploy until a new one builds and passes
its health check (`GET /health`).

Everything resolves to one hostname. Unknown paths fall back to `index.html`
(see `docker/nginx.conf.template`), so old `/order` and `/admin` links land
on the home page rather than 404ing.

### One-time cleanup still owed

Removing services from a blueprint does not delete them on Render. The old
`boithok-api` and `boithok-db` are still sitting in the dashboard — **delete
them by hand**, otherwise the free database keeps counting down its 30-day
deletion clock and the API keeps eating free instance hours whenever
something wakes it.

### DNS

Unchanged: GoDaddy points `www` and the apex at the Render service. Moving
hosts means re-pointing those records and re-adding the custom domains in
Render.

## Keeping it awake

Free Render services spin down after 15 minutes without traffic and take
about a minute to wake, which is why a first visitor sometimes saw Render's
loading screen.

`.github/workflows/keep-warm.yml` runs `scripts/keep-warm.sh` every 10
minutes between 15:00 and 01:59 UTC (roughly 11am–10pm in Toronto). Outside
that window the site sleeps on purpose.

**The window is a budget, not a preference.** A Render workspace gets 750
free instance-hours per calendar month, shared across every free service in
it. 11 hours/day × 31 days = 341 hours. Go to 24/7 and it's 744 — one wobble
over the line and Render suspends the service until the next month. Redo the
arithmetic before widening the cron.

The scheduled workflow only runs from the repository's **default branch**
(`main`), so keep `main` up to date with the deploy branch.

Run it by hand any time:

```bash
scripts/keep-warm.sh
```

A non-zero exit means the site is genuinely unreachable — every target is
retried three times through a full cold start before it fails.

### The permanent fix

Either upgrade `boithok-web` to Render's `starter` plan, or move the site to
a Render **static site** (free, never sleeps — it would need a new service
and the custom domains moved onto it in the dashboard). Either way,
`.github/workflows/keep-warm.yml` and `scripts/keep-warm.sh` can then be
deleted.
