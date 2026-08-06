/**
 * Same-origin proxy to the FastAPI backend.
 *
 * In production the whole site is one hostname (www.boithokkhana.ca): the
 * marketing page, /order, /admin, and the API under /api. The browser never
 * makes a cross-origin request, so CORS never enters the picture and the
 * backend needs no public URL of its own.
 *
 * This is a route handler rather than a next.config rewrite on purpose:
 * rewrites are resolved at build time and baked into the routes manifest,
 * whereas the backend's address (BACKEND_ORIGIN) is only known at runtime on
 * Render. Reading it per-request also means changing it needs a restart, not
 * a rebuild.
 *
 * Local dev: BACKEND_ORIGIN is unset and NEXT_PUBLIC_API_URL points the
 * browser straight at localhost:8000, so this handler simply isn't used.
 */
import { NextRequest, NextResponse } from "next/server";

// Always run per-request: the backend's responses are order data, never static.
export const dynamic = "force-dynamic";

/** Render supplies "host:port" with no scheme; normalise to a full origin. */
function backendOrigin(): string | null {
  const raw = process.env.BACKEND_ORIGIN?.trim();
  if (!raw) return null;
  return /^https?:\/\//.test(raw) ? raw : `http://${raw}`;
}

/** Headers worth forwarding upstream. Hop-by-hop and host headers are not. */
const FORWARDED_REQUEST_HEADERS = ["content-type", "accept", "x-admin-pin"];

async function proxy(request: NextRequest): Promise<Response> {
  const origin = backendOrigin();
  if (!origin) {
    // Misconfiguration, not a customer error — say so plainly rather than
    // returning a confusing 404 that looks like a missing page.
    return NextResponse.json(
      { detail: "API proxy is not configured (BACKEND_ORIGIN is unset)." },
      { status: 503 },
    );
  }

  const { pathname, search } = request.nextUrl;
  const target = `${origin}${pathname}${search}`;

  const headers = new Headers();
  for (const name of FORWARDED_REQUEST_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  const hasBody = request.method !== "GET" && request.method !== "HEAD";

  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      // Surface the backend's own redirects/errors verbatim.
      redirect: "manual",
      cache: "no-store",
    });

    const responseHeaders = new Headers();
    const contentType = upstream.headers.get("content-type");
    if (contentType) responseHeaders.set("content-type", contentType);
    const disposition = upstream.headers.get("content-disposition");
    // CSV export relies on this to trigger a download with the right filename.
    if (disposition) responseHeaders.set("content-disposition", disposition);

    return new Response(upstream.body, {
      status: upstream.status,
      statusText: upstream.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    // Log the real cause: the customer sees a friendly message, but without
    // this the server logs show nothing at all and the failure is
    // undiagnosable. (Learned the hard way during the first deploy.)
    console.error(
      `[api-proxy] ${request.method} ${target} failed:`,
      error instanceof Error ? `${error.name}: ${error.message}` : error,
      error instanceof Error && error.cause ? `cause: ${String(error.cause)}` : "",
    );
    // The API is down or unreachable. An order must never look "submitted"
    // when it wasn't, so this is an explicit failure the UI can show.
    return NextResponse.json(
      { detail: "Could not reach the order service. Please try again." },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
