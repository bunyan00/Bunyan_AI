/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'arabic': ['Noto Sans Arabic', 'Arial', 'sans-serif'],
      },
      spacing: {
        'rtl': '0 0 0 auto',
      },
      animation: {
        'bounce-rtl': 'bounce-rtl 1s infinite',
      },
    },
  },
  plugins: [],
};