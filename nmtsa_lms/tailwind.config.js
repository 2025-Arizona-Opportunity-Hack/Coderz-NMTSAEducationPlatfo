/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './nmtsa_lms/templates/**/*.html',
    './student_dash/templates/**/*.html',
    './teacher_dash/templates/**/*.html',
    './admin_dash/templates/**/*.html',
    './lms/templates/**/*.html',
    './authentication/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Brand color palette - NMTSA Theme
        brand: {
          gold: '#CC9300',        // Primary gold
          'gold-light': '#FFD966', // Light gold for backgrounds
          'gold-dark': '#996D00',  // Dark gold for hover states
          orange: '#CB6000',      // Secondary orange
          'orange-light': '#FF9947', // Light orange
          'orange-dark': '#964800',  // Dark orange
          purple: '#3C0182',      // Accent purple
          'purple-light': '#7B4FD1', // Light purple
          'purple-dark': '#2A005C',  // Dark purple
        },
        // Light theme
        light: {
          bg: '#FFFFFF',
          'bg-secondary': '#F8F9FA',
          text: '#1A1A1A',
          'text-muted': '#6C757D',
          border: '#DEE2E6',
        },
        // Dark theme
        dark: {
          bg: '#1A1A1A',
          'bg-secondary': '#2D2D2D',
          text: '#F8F9FA',
          'text-muted': '#ADB5BD',
          border: '#495057',
        },
        // High contrast theme
        contrast: {
          bg: '#FFFFFF',
          text: '#000000',
          border: '#000000',
          focus: '#0000FF',
        },
        // Semantic colors (WCAG AAA compliant)
        semantic: {
          success: '#0F6E0F',      // Green
          'success-bg': '#D4EDDA',
          info: '#004085',          // Blue
          'info-bg': '#CCE5FF',
          warning: '#856404',       // Amber
          'warning-bg': '#FFF3CD',
          error: '#721C24',         // Red
          'error-bg': '#F8D7DA',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1.5' }],
        'sm': ['0.875rem', { lineHeight: '1.5' }],
        'base': ['1rem', { lineHeight: '1.6' }],
        'lg': ['1.125rem', { lineHeight: '1.6' }],
        'xl': ['1.25rem', { lineHeight: '1.6' }],
        '2xl': ['1.5rem', { lineHeight: '1.4' }],
        '3xl': ['1.875rem', { lineHeight: '1.3' }],
        '4xl': ['2.25rem', { lineHeight: '1.2' }],
        '5xl': ['3rem', { lineHeight: '1.1' }],
      },
      spacing: {
        'tight': '0.5rem',      // 8px
        'normal': '1rem',       // 16px
        'relaxed': '1.5rem',    // 24px
        'loose': '2rem',        // 32px
      },
      maxWidth: {
        'content': '1200px',
        'prose': '65ch',
      },
      screens: {
        'xs': '475px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
      // Disable all animations by default for autism-friendly design
      transitionDuration: {
        DEFAULT: '0ms',
      },
      transitionProperty: {
        DEFAULT: 'none',
      },
      // Minimum touch target sizes (44x44px for accessibility)
      minHeight: {
        'touch': '44px',
      },
      minWidth: {
        'touch': '44px',
      },
    },
  },
  plugins: [],
  // Disable all animations globally for autism-friendly design
  corePlugins: {
    animation: false,
  },
}
