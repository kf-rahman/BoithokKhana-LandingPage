/**
 * Next.js instrumentation hook — loads the right Sentry config per runtime.
 * Both are inert unless SENTRY_DSN is set.
 */
export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }
  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }
}
