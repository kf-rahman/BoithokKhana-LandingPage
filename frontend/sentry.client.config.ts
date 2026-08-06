/**
 * Sentry — browser errors (the order form and the admin dashboard).
 *
 * Disabled until NEXT_PUBLIC_SENTRY_DSN is set. Note this is a NEXT_PUBLIC_*
 * var: it is inlined into the client bundle at build time, so setting it on
 * Render requires a redeploy to take effect.
 *
 * Privacy: customers type names, phones and delivery notes into the order box.
 * sendDefaultPii stays false and text is masked in any replay, so that content
 * is not shipped off to debug a crash.
 */
import * as Sentry from "@sentry/nextjs";

const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT ?? "development",
    // Errors only — keeps the free tier's quota for things that are broken.
    tracesSampleRate: 0,
    sendDefaultPii: false,
    // No session replay: it would record the customer's order text verbatim.
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0,
  });
}
