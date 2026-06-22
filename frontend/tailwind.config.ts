import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  // globals.css carries the Boithok Khana brand CSS (with its own reset), so
  // keep Tailwind's utilities available but disable preflight — otherwise its
  // base reset fights the hand-written styles we're preserving verbatim.
  corePlugins: { preflight: false },
  theme: {
    extend: {
      colors: {
        "primary-red": "#DC2626",
        "deep-red": "#991B1B",
        "bright-orange": "#FF8C00",
        "golden-yellow": "#FACC15",
        "dark-green": "#006400",
        "fresh-green": "#22C55E",
        "deep-green": "#15803D",
        cream: "#FFFBEB",
        "brand-dark": "#1F2937",
        "light-gray": "#F3F4F6",
      },
    },
  },
  plugins: [],
};

export default config;
