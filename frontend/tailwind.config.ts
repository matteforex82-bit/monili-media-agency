import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        gold: '#D4AF37',
        'gold-bright': '#F0CB50',
        'gold-dim': '#8B7020',
        'neon-green': '#39FF14',
        'neon-blue': '#00D4FF',
        'neon-orange': '#FF6B35',
        'agency-bg': '#080808',
        'agency-card': '#0F0F0F',
        'agency-card-2': '#141414',
        'agency-border': 'rgba(255,255,255,0.06)',
      },
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        grotesk: ['Space Grotesk', 'sans-serif'],
        mono: ['Space Mono', 'monospace'],
      },
      animation: {
        'pulse-gold': 'pulseGold 2s ease-in-out infinite',
        'blink': 'blink 1s step-end infinite',
        'scan': 'scan 3s linear infinite',
        'glow-in': 'glowIn 0.4s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'progress': 'progress 1.5s ease-in-out',
      },
      keyframes: {
        pulseGold: {
          '0%, 100%': { boxShadow: '0 0 8px rgba(212,175,55,0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(212,175,55,0.7), 0 0 40px rgba(212,175,55,0.3)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        glowIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
