import type { Config } from "tailwindcss";

// Preflight is disabled so Tailwind's reset doesn't clobber the brand
// styles lifted from index.html.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  corePlugins: { preflight: false },
  theme: { extend: {} },
  plugins: [],
};

export default config;
