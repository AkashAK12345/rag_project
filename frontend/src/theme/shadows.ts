// src/theme/shadows.ts
// GROVIT AI — Elevation shadows
// Uses soft, diffuse shadows to create depth without harsh borders.

export const shadows = {
  /** Subtle card resting shadow */
  card: '0px 1px 3px rgba(0,0,0,0.06), 0px 4px 16px rgba(0,0,0,0.06)',

  /** Card hover lift */
  cardHover: '0px 4px 12px rgba(0,0,0,0.08), 0px 12px 32px rgba(0,0,0,0.10)',

  /** Sidebar right shadow */
  sidebar: '4px 0px 24px rgba(0,0,0,0.07)',

  /** Top navigation bar bottom shadow */
  topbar: '0px 1px 0px rgba(0,0,0,0.06), 0px 4px 12px rgba(0,0,0,0.04)',

  /** Floating elements — dialogs, menus */
  floating: '0px 8px 24px rgba(0,0,0,0.12), 0px 2px 8px rgba(0,0,0,0.08)',

  /** Input focus ring shadow */
  inputFocus: '0 0 0 3px rgba(249,115,22,0.15)',

  /** Button primary (orange) */
  buttonPrimary: '0px 4px 14px rgba(249,115,22,0.35)',

  /** No shadow */
  none: 'none',
} as const;
