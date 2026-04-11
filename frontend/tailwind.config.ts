import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#f5f2eb",
        foreground: "#18211f",
        muted: {
          DEFAULT: "#dcd7cb",
          foreground: "#67756d",
        },
        card: "#fffdf8",
        border: "rgba(24, 33, 31, 0.08)",
        primary: {
          DEFAULT: "#0f766e",
          foreground: "#f4fffc",
        },
        secondary: {
          DEFAULT: "#ece7dc",
          foreground: "#18211f",
        },
        accent: {
          DEFAULT: "#f0f7f5",
          foreground: "#0f5d57",
        },
      },
      borderRadius: {
        xl: "1.25rem",
        "2xl": "1.75rem",
        "3xl": "2rem",
      },
      boxShadow: {
        soft: "0 18px 50px rgba(18, 25, 24, 0.08)",
      },
      fontFamily: {
        display: ['"Iowan Old Style"', '"Palatino Linotype"', "serif"],
        sans: ["Inter", "Segoe UI", "Helvetica Neue", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
