/**
 * Sentry — edge runtime (middleware). Nothing runs here today, but the SDK
 * expects the file to exist. Disabled until SENTRY_DSN is set.
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
