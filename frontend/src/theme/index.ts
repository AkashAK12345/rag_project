// src/theme/index.ts
import { createTheme, type PaletteMode } from '@mui/material';

// ── Design tokens ────────────────────────────────────────────────────────────
const SIDEBAR_WIDTH = 240;
const SIDEBAR_COLLAPSED_WIDTH = 64;

export { SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH };

// ── Colour palette ───────────────────────────────────────────────────────────
const palette = {
  primary: { main: '#6366F1', light: '#818CF8', dark: '#4338CA' }, // indigo
  secondary: { main: '#0EA5E9', light: '#38BDF8', dark: '#0284C7' }, // sky
  success: { main: '#10B981', dark: '#059669' },
  warning: { main: '#F59E0B', dark: '#D97706' },
  error: { main: '#EF4444', dark: '#DC2626' },
};

export const createAppTheme = (mode: PaletteMode) =>
  createTheme({
    palette: {
      mode,
      primary: palette.primary,
      secondary: palette.secondary,
      success: palette.success,
      warning: palette.warning,
      error: palette.error,
      background:
        mode === 'dark'
          ? { default: '#0F172A', paper: '#1E293B' }
          : { default: '#F8FAFC', paper: '#FFFFFF' },
      text:
        mode === 'dark'
          ? { primary: '#F1F5F9', secondary: '#94A3B8' }
          : { primary: '#0F172A', secondary: '#64748B' },
      divider: mode === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
    },

    typography: {
      fontFamily: '"Inter", "Segoe UI", system-ui, sans-serif',
      h1: { fontWeight: 700, fontSize: '2rem', letterSpacing: '-0.02em' },
      h2: { fontWeight: 700, fontSize: '1.5rem', letterSpacing: '-0.01em' },
      h3: { fontWeight: 600, fontSize: '1.25rem' },
      h4: { fontWeight: 600, fontSize: '1.125rem' },
      h5: { fontWeight: 600, fontSize: '1rem' },
      h6: { fontWeight: 600, fontSize: '0.875rem' },
      body1: { fontSize: '0.9375rem', lineHeight: 1.6 },
      body2: { fontSize: '0.875rem', lineHeight: 1.5 },
      caption: { fontSize: '0.75rem' },
    },

    shape: { borderRadius: 10 },

    components: {
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: { textTransform: 'none', fontWeight: 600, borderRadius: 8 },
        },
      },
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: ({ theme }) => ({
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 12,
          }),
        },
      },
      MuiChip: {
        styleOverrides: { root: { fontWeight: 600 } },
      },
      MuiTableCell: {
        styleOverrides: {
          head: ({ theme }) => ({
            fontWeight: 600,
            fontSize: '0.75rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: theme.palette.text.secondary,
            borderBottom: `1px solid ${theme.palette.divider}`,
          }),
        },
      },
      MuiLinearProgress: {
        styleOverrides: { root: { borderRadius: 4, height: 6 } },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: { borderRadius: 8, margin: '2px 8px' },
        },
      },
      MuiTooltip: {
        defaultProps: { arrow: true, placement: 'right' },
      },
    },
  });
