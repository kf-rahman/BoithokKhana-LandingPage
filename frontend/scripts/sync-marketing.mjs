/**
 * Copies the marketing site (root `index.html`) into `public/site.html` so the
 * Next.js server can serve it at `/` (see the rewrite in next.config.mjs).
 *
 * The root `index.html` stays the single source of truth — edit it there, not
 * here. This runs automatically before `dev` and `build`; the copy is
 * gitignored so the two can never drift in a commit.
 */
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "../../index.html");
const destination = resolve(here, "../public/site.html");

if (!existsSync(source)) {
  console.error(
    `[sync-marketing] Expected the marketing page at ${source}, but it is missing.\n` +
      `The site's "/" route is served from that file. Restore it before building.`,
  );
  process.exit(1);
}

mkdirSync(dirname(destination), { recursive: true });
copyFileSync(source, destination);
console.log("[sync-marketing] index.html -> public/site.html");
