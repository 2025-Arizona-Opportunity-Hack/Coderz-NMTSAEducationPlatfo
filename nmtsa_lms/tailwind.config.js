/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './nmtsa_lms/templates/**/*.html',
    './student_dash/templates/**/*.html',
    './teacher_dash/templates/**/*.html',
    './admin_dash/templates/**/*.html',
    './lms/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Autism-friendly color palette - "Calm Therapy"
        primary: {
          soft: '#A8C5DA',      // pale blue
          medium: '#7FA8C9',    // soft sky blue
          DEFAULT: '#7FA8C9',
        },
        earth: {
          sage: '#B5C3A8',      // soft sage green
          sand: '#D9C9B3',      // warm sand
        },
        neutral: {
          light: '#F5F5F0',     // off-white, warm
          medium: '#D9D9D4',    // soft gray
          dark: '#5A5A52',      // muted charcoal
          DEFAULT: '#D9D9D4',
        },
        accent: {
          success: '#A8C9A8',   // muted green
          info: '#B8D4E6',      // soft info blue
          warning: '#E6D8B8',   // muted amber
        },
        // Dark theme colors
        dark: {
          bg: '#3A3A35',
          card: '#4A4A45',
          text: '#E5E5E0',
        },
      },
      fontFamily: {
        sans: ['Arial', 'Helvetica', 'sans-serif'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1.5' }],
        'sm': ['0.875rem', { lineHeight: '1.5' }],
        'base': ['1rem', { lineHeight: '1.6' }],
        'lg': ['1.25rem', { lineHeight: '1.6' }],
        'xl': ['1.5rem', { lineHeight: '1.6' }],
        '2xl': ['2rem', { lineHeight: '1.4' }],
      },
      spacing: {
        'tight': '8px',
        'normal': '16px',
        'relaxed': '24px',
        'loose': '32px',
      },
      maxWidth: {
        'content': '1200px',
      },
      // Disable all animations by default
      transitionDuration: {
        DEFAULT: '0ms',
      },
      transitionProperty: {
        DEFAULT: 'none',
      },
    },
  },
  plugins: [],
  // Disable all animations globally for autism-friendly design
  corePlugins: {
    animation: false,
  },
}
