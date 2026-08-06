/**
 * Sentry — errors thrown while rendering on the Next.js server.
 * Disabled until SENTRY_DSN is set. See sentry.client.config.ts for the
 * privacy rationale.
 */
import * as Sentry from "@sentry/nextjs";

const dsn = process.env.SENTRY_DSN;

if (dsn) {
  Sentry.init({
    dsn,
    environment: process.env.SENTRY_ENVIRONMENT ?? "development",
    tracesSampleRate: 0,
    sendDefaultPii: false,
  });
}
