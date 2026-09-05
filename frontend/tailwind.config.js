/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2E7D32',
        darkGreen: '#1B5E20',
        lightGreen: '#E8F5E9',
        bgGreen: '#F8FAF8',
        appText: '#1F2937',
        warning: '#F59E0B',
        danger: '#DC2626',
        success: '#16A34A',
        brand: {
          50: '#F8FAF8',
          100: '#E8F5E9',
          200: '#C8E6C9',
          500: '#2E7D32',
          600: '#276A2B',
          700: '#1B5E20',
          800: '#144A18',
          900: '#0E3611',
        }
      }
    },
  },
  plugins: [],
}
