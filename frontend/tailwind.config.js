/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#135bec",
        "background-light": "#f6f6f8",
        "background-dark": "#101622",
        "surface-light": "#ffffff",
        "surface-dark": "#1a2230",
      },
      fontFamily: {
        "display": ["Work Sans", "sans-serif"],
        "sans": ["Work Sans", "sans-serif"], // Override default sans
      },
      borderRadius: {
        "xl": "0.75rem",
        "2xl": "1rem",
      }
    },
  },
  plugins: [],
}