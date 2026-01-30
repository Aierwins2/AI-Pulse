/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pulse-primary': '#6366f1',
        'pulse-secondary': '#8b5cf6',
        'pulse-tech': '#3b82f6',
        'pulse-benchmark': '#10b981',
        'pulse-product': '#f59e0b',
        'pulse-insights': '#ef4444',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
