# Spec: Deployment artifacts

## Goal

Make the app deployable: a containerised backend and a Compose file wiring
it to Postgres, matching the other workflows. (AGENTS.md said "no deploy
config unless asked" — this is the ask.)

## Constraints

- Local dev still runs on SQLite with no Docker. Postgres via Compose for a
  deploy-like run. No secrets committed.

## Acceptance criteria

- [x] `backend/Dockerfile` builds and runs uvicorn.
- [x] `docker-compose.yml` runs Postgres + the API against it
      (`DATABASE_URL=postgresql+psycopg://…`).
- [x] `backend/.dockerignore` excludes venv / db / env / tests.
- [x] A README note covers both run modes.

## Out of scope

- Vercel / frontend hosting config; CI/CD.

## Open questions

- None.
