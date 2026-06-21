# Frontend — Family Catering Order System (Next.js)

## Setup

```
npm install
cp .env.local.example .env.local     # optional; defaults to http://localhost:8000
```

## Run

```
npm run dev        # http://localhost:3000
```

The home page pings the backend's `/health` endpoint and shows whether it's
reachable — start the backend (`uvicorn app.main:app --reload`) to see it go green.

## Checks

```
npm run type-check
npm run lint
```

## Pages

- `/` — skeleton home + backend health indicator
- `/order` — customer free-text order form (TODO)
- `/admin` — Dad-facing dashboard (TODO)
