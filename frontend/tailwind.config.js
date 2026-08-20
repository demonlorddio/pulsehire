/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          0: '#09090b',
          1: '#0f0f11',
          2: '#18181b',
          3: '#27272a',
          4: '#3f3f46',
        },
        accent: {
          DEFAULT: '#f59e0b',
          dim: '#b45309',
          bright: '#fbbf24',
          muted: 'rgba(245,158,11,0.08)',
        },
        muted: '#71717a',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        'display': ['3rem', { lineHeight: '1.1', fontWeight: '800' }],
        'title': ['1.5rem', { lineHeight: '1.2', fontWeight: '700' }],
        'metric': ['2rem', { lineHeight: '1', fontWeight: '800', fontFeatureSettings: '"tnum"' }],
      },
    },
  },
  plugins: [],
}
