// src/theme/index.ts
// GROVIT AI — Master theme composer
// Imports all design tokens and builds the MUI theme for light and dark modes.

import { createTheme, type PaletteMode } from '@mui/material';
import { brand, neutral, semantic, dark } from './colors';
import { fontFamily, typeScale } from './typography';
import { spacing } from './spacing';
import { radius } from './radius';
import { shadows as appShadows } from './shadows';
import { durations, easings } from './transitions';

// Re-export layout constants consumed by AppLayout
export const SIDEBAR_WIDTH          = spacing.sidebarWidth;
export const SIDEBAR_COLLAPSED_WIDTH = spacing.sidebarCollapsedWidth;

export const createAppTheme = (mode: PaletteMode) => {
  const isLight = mode === 'light';

  return createTheme({
    // ── Palette ──────────────────────────────────────────────────────────────
    palette: {
      mode,
      primary: {
        main:         brand.orange,
        light:        brand.orangeLight,
        dark:         brand.orangeDark,
        contrastText: neutral.white,
      },
      secondary: {
        main:         semantic.info,
        light:        '#60A5FA',
        dark:         semantic.infoDark,
        contrastText: neutral.white,
      },
      success: {
        main:         semantic.success,
        dark:         semantic.successDark,
        contrastText: neutral.white,
      },
      warning: {
        main:         semantic.warning,
        dark:         semantic.warningDark,
        contrastText: neutral.white,
      },
      error: {
        main:         semantic.error,
        dark:         semantic.errorDark,
        contrastText: neutral.white,
      },
      background: isLight
        ? { default: neutral[50], paper: neutral.white }
        : { default: dark.background, paper: dark.paper },
      text: isLight
        ? { primary: neutral[800], secondary: neutral[500] }
        : { primary: dark.textPrimary, secondary: dark.textSecondary },
      divider: isLight ? 'rgba(0,0,0,0.06)' : dark.border,
    },

    // ── Typography ────────────────────────────────────────────────────────────
    typography: {
      fontFamily,
      ...typeScale,
    },

    // ── Shape ─────────────────────────────────────────────────────────────────
    shape: { borderRadius: radius.card },

    // ── Transitions ───────────────────────────────────────────────────────────
    transitions: {
      duration:  { shortest: durations.fast, short: durations.fast, standard: durations.normal, complex: durations.slow, enteringScreen: durations.normal, leavingScreen: durations.fast },
      easing:    { easeInOut: easings.standard, easeOut: easings.decelerate, easeIn: easings.accelerate, sharp: easings.sharp },
    },

    // ── Component overrides ───────────────────────────────────────────────────
    components: {
      // Button
      MuiButton: {
        defaultProps: { disableElevation: true },
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 600,
            borderRadius: radius.button,
            transition: `all ${durations.normal}ms ${easings.standard}`,
          },
          contained: {
            '&.MuiButton-containedPrimary': {
              boxShadow: appShadows.buttonPrimary,
              '&:hover': {
                boxShadow: appShadows.cardHover,
                transform: 'translateY(-1px)',
              },
            },
          },
          outlined: {
            '&.MuiButton-outlinedPrimary': {
              borderColor: brand.orange,
              '&:hover': {
                backgroundColor: brand.orangeSubtle,
              },
            },
          },
        },
      },

      // Card
      MuiCard: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            borderRadius: radius.card,
            boxShadow: appShadows.card,
            border: 'none',
            transition: `box-shadow ${durations.normal}ms ${easings.standard}, transform ${durations.normal}ms ${easings.standard}`,
          },
        },
      },

      // Paper
      MuiPaper: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
          rounded: {
            borderRadius: radius.card,
          },
        },
      },

      // TextField / Input
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: radius.input,
            transition: `box-shadow ${durations.fast}ms ${easings.standard}`,
            '&.Mui-focused': {
              boxShadow: appShadows.inputFocus,
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: brand.orange,
                borderWidth: '1.5px',
              },
            },
          },
          notchedOutline: {
            borderColor: isLight ? neutral[200] : dark.border,
          },
        },
      },

      // Chip
      MuiChip: {
        styleOverrides: {
          root: {
            fontWeight: 600,
            borderRadius: radius.chip,
          },
        },
      },

      // ListItemButton (sidebar nav pills)
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: radius.navPill,
            transition: `all ${durations.fast}ms ${easings.standard}`,
          },
        },
      },

      // Divider
      MuiDivider: {
        styleOverrides: {
          root: {
            borderColor: isLight ? neutral[100] : dark.border,
          },
        },
      },

      // Table
      MuiTableCell: {
        styleOverrides: {
          head: ({ theme }) => ({
            fontWeight: 700,
            fontSize: '0.6875rem',
            textTransform: 'uppercase',
            letterSpacing: '0.08em',
            color: theme.palette.text.secondary,
            backgroundColor: isLight ? neutral[50] : dark.elevated,
            borderBottom: `1px solid ${isLight ? neutral[100] : dark.border}`,
          }),
          body: {
            fontSize: '0.875rem',
            borderBottom: `1px solid ${isLight ? neutral[100] : dark.border}`,
          },
        },
      },

      // LinearProgress
      MuiLinearProgress: {
        styleOverrides: {
          root: { borderRadius: radius.full, height: 6 },
        },
      },

      // Tooltip
      MuiTooltip: {
        defaultProps: { arrow: true },
        styleOverrides: {
          tooltip: {
            borderRadius: radius.tooltip,
            fontSize: '0.75rem',
            fontWeight: 500,
          },
        },
      },

      // Dialog
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: radius.card,
            boxShadow: appShadows.floating,
          },
        },
      },

      // AppBar
      MuiAppBar: {
        defaultProps: { elevation: 0 },
        styleOverrides: {
          root: {
            boxShadow: appShadows.topbar,
          },
        },
      },
    },
  });
};
