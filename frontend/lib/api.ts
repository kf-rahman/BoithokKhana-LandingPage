/**
 * Base URL the browser uses to reach the FastAPI backend.
 *
 * In production this is the empty string, i.e. same-origin: the browser calls
 * `/api/...` on whatever host it loaded the page from, and
 * `app/api/[...path]/route.ts` proxies that to the backend. One hostname, no
 * CORS, and nothing host-specific compiled into the bundle.
 *
 * Do NOT make this fall back to a localhost URL in production. NEXT_PUBLIC_*
 * values are inlined into the client bundle at build time, so a localhost
 * default ships to real visitors and every request fails against their own
 * machine — which is exactly what happened on the first deploy. Keying the
 * default off NODE_ENV (rather than an env var that may be unset or empty at
 * build time) makes the production behaviour independent of how the host
 * passes build arguments.
 *
 * Set NEXT_PUBLIC_API_URL explicitly to override — e.g. docker-compose points
 * it at http://localhost:8000 so the browser reaches the API's published port.
 */
const configured = process.env.NEXT_PUBLIC_API_URL;

export const API_BASE_URL =
  configured !== undefined && configured !== ""
    ? configured
    : process.env.NODE_ENV === "production"
      ? "" // same-origin; proxied by app/api/[...path]/route.ts
      : "http://localhost:8000";
