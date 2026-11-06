import type { Config } from "tailwindcss";

import { borderRadius, boxShadow } from "./tokens";

const withAlpha = (variable: string) => `rgb(var(${variable}) / <alpha-value>)`;

export const tailwindPreset: Partial<Config> = {
  theme: {
    extend: {
      colors: {
        background: withAlpha("--background"),
        surface: withAlpha("--surface"),
        sunken: withAlpha("--sunken"),
        ink: withAlpha("--ink"),
        muted: withAlpha("--muted"),
        line: withAlpha("--line"),
        stroke: {
          DEFAULT: withAlpha("--stroke"),
          hover: withAlpha("--stroke-hover"),
        },
        accent: {
          DEFAULT: withAlpha("--accent"),
          soft: withAlpha("--accent-soft"),
        },
        highlight: {
          DEFAULT: withAlpha("--highlight"),
          hover: withAlpha("--highlight-hover"),
        },
        danger: withAlpha("--danger"),
        success: withAlpha("--success"),
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "var(--font-sans)", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius,
      boxShadow,
      keyframes: {
        "fade-in": { from: { opacity: "0", transform: "translateY(4px)" }, to: { opacity: "1" } },
        shimmer: { from: { backgroundPosition: "200% 0" }, to: { backgroundPosition: "-200% 0" } },
        scan: { from: { transform: "translateY(-100%)" }, to: { transform: "translateY(400%)" } },
        indeterminate: {
          from: { transform: "translateX(-100%)" },
          to: { transform: "translateX(300%)" },
        },
      },
      animation: {
        "fade-in": "fade-in 240ms ease-out",
        shimmer: "shimmer 1.6s linear infinite",
        scan: "scan 2.4s ease-in-out infinite alternate",
        indeterminate: "indeterminate 1.4s ease-in-out infinite",
      },
    },
  },
};
