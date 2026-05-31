/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        bci: {
          cyan: "#22d3ee",
          violet: "#a78bfa",
        },
      },
    },
  },
  plugins: [],
};
