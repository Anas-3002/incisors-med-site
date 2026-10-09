/** Tailwind config taken verbatim from the Stitch export's inline <script id="tailwind-config">,
 *  with the content globs pointed at this repo's HTML/JS (the export used the Play CDN,
 *  which compiles the same config in the browser). */
module.exports = {
  darkMode: "class",
  content: ["./*.html", "./assets/js/*.js"],
  theme: {
    extend: {
      colors: {
        "primary": "#0A2540",
        "primary-light": "#1E3A8A",
        "secondary": "#06B6D4",
        "secondary-dark": "#0891B2",
        "accent-teal": "#0D9488",
        "accent-cyan": "#00F0FF",
        "surface": "#F8FAFC",
        "surface-card": "#FFFFFF",
        "brand-emerald": "#10B981",
        "brand-purple": "#8B5CF6",
        "brand-amber": "#F59E0B"
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "sans-serif"]
      }
    }
  },
  plugins: [require("@tailwindcss/forms"), require("@tailwindcss/container-queries")]
};
