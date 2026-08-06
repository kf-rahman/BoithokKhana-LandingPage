import { withSentryConfig } from "@sentry/nextjs";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Required on Next 14 for instrumentation.ts (the Sentry server hook) to run.
  experimental: { instrumentationHook: true },

  // The marketing site (root `index.html`, copied to `public/site.html` by
  // scripts/sync-marketing.mjs) is served at "/". A `beforeFiles` rewrite is
  // required here: it runs ahead of the App Router, so it wins over
  // `app/page.tsx`. The ordering app keeps /order and /admin.
  // Note: the /api proxy is NOT a rewrite. Rewrites are evaluated at build
  // time and frozen into routes-manifest.json, but the backend's address is
  // only known at runtime on Render. It's a route handler instead —
  // app/api/[...path]/route.ts.
  async rewrites() {
    return {
      beforeFiles: [{ source: "/", destination: "/site.html" }],
      afterFiles: [],
      fallback: [],
    };
  },
};

// Wrapping is harmless with no DSN configured — the SDK no-ops. Source maps
// are only uploaded when SENTRY_AUTH_TOKEN/org/project are present, so builds
// stay quiet and fast until you finish the Sentry setup.
export default withSentryConfig(nextConfig, {
  silent: true,
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  // Don't fail a deploy because error reporting couldn't upload source maps.
  errorHandler: () => {},
  disableLogger: true,
});
