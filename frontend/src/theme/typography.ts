// src/theme/typography.ts
// GROVIT AI — Typography tokens

export const fontFamily = '"Inter", "Segoe UI", system-ui, -apple-system, sans-serif';

export const fontWeights = {
  regular: 400,
  medium:  500,
  semibold: 600,
  bold:    700,
  extrabold: 800,
} as const;

export const typeScale = {
  h1: { fontSize: '2.25rem',  fontWeight: 800, lineHeight: 1.2,  letterSpacing: '-0.03em' },
  h2: { fontSize: '1.875rem', fontWeight: 700, lineHeight: 1.25, letterSpacing: '-0.02em' },
  h3: { fontSize: '1.5rem',   fontWeight: 700, lineHeight: 1.3,  letterSpacing: '-0.015em' },
  h4: { fontSize: '1.25rem',  fontWeight: 600, lineHeight: 1.35, letterSpacing: '-0.01em' },
  h5: { fontSize: '1.125rem', fontWeight: 600, lineHeight: 1.4  },
  h6: { fontSize: '1rem',     fontWeight: 600, lineHeight: 1.5  },
  body1: { fontSize: '0.9375rem', lineHeight: 1.65 },
  body2: { fontSize: '0.875rem',  lineHeight: 1.6  },
  caption: { fontSize: '0.75rem', lineHeight: 1.5  },
  overline: { fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' as const },
} as const;
