/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './hooks/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a6996',
        'primary-hover': '#013E62',
        'primary-light': '#E8F3FB',
        accent: '#D9454C',
        'accent-hover': '#B83940',
        'accent-light': '#FDECED',
        surface: '#F5F6FA',
        border: '#E2E4E9',
        muted: '#6B7280',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
};
