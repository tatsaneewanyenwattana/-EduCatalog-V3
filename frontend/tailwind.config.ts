import type { Config } from "tailwindcss";

// สี/รัศมีมาจาก CSS variables (กฎ G5) — ไม่ hardcode สีใน class แบบ arbitrary
const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "var(--color-primary)",
          dark: "var(--color-primary-dark)",
          light: "var(--color-primary-light)",
          foreground: "var(--color-primary-foreground)",
        },
        accent: {
          DEFAULT: "var(--color-accent)",
          dark: "var(--color-accent-dark)",
        },
        surface: "var(--color-surface)",
        border: "var(--color-border)",
        error: "var(--color-error)",
        warning: "var(--color-warning)",
        success: "var(--color-success)",
        foreground: {
          DEFAULT: "var(--color-text)",
          secondary: "var(--color-text-secondary)",
        },
        page: "var(--color-bg)",
        footer: {
          bg: "var(--color-footer-bg)",
          fg: "var(--color-footer-fg)",
          muted: "var(--color-footer-muted)",
        },
      },
      fontFamily: {
        sans: ["var(--font-kanit)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      fontSize: {
        xs: ["var(--text-xs)", { lineHeight: "1.5" }],
        sm: ["var(--text-sm)", { lineHeight: "1.6" }],
        base: ["var(--text-base)", { lineHeight: "1.7" }],
        lg: ["var(--text-lg)", { lineHeight: "1.6" }],
        xl: ["var(--text-xl)", { lineHeight: "1.4" }],
        "2xl": ["var(--text-2xl)", { lineHeight: "1.3" }],
      },
      borderRadius: {
        DEFAULT: "var(--radius)",
        none: "var(--radius)",
        sm: "var(--radius)",
        md: "var(--radius)",
        lg: "var(--radius)",
        full: "var(--radius)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
      },
      spacing: {
        1: "var(--space-1)",
        2: "var(--space-2)",
        3: "var(--space-3)",
        4: "var(--space-4)",
        6: "var(--space-6)",
        8: "var(--space-8)",
        12: "var(--space-12)",
        16: "var(--space-16)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
