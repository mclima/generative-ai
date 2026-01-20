import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#000000",
        foreground: "#ffffff",
        primary: {
          DEFAULT: "#3b82f6",
          dark: "#2563eb",
        },
        success: "#10b981",
        danger: "#ef4444",
        warning: "#f59e0b",
        info: "#06b6d4",
      },
    },
  },
  plugins: [],
};
export default config;
