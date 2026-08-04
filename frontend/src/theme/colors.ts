// src/theme/colors.ts
// GROVIT AI — Canonical colour tokens
// All palette values must reference these constants. No hardcoded hex values elsewhere.

export const brand = {
  orange:       '#F97316',
  orangeLight:  '#FDBA74',
  orangeDark:   '#EA6C04',
  orangeSubtle: '#FFF7ED',
} as const;

export const neutral = {
  white:   '#FFFFFF',
  50:      '#F6F8FB',
  100:     '#EEF1F6',
  200:     '#E2E7EF',
  300:     '#CBD3E0',
  400:     '#9CA8B8',
  500:     '#6B7280',
  600:     '#4B5563',
  700:     '#374151',
  800:     '#1F2937',
  900:     '#111827',
  black:   '#000000',
} as const;

export const semantic = {
  success: '#22C55E',
  successDark: '#16A34A',
  successSubtle: '#F0FDF4',

  warning: '#F59E0B',
  warningDark: '#D97706',
  warningSubtle: '#FFFBEB',

  error: '#EF4444',
  errorDark: '#DC2626',
  errorSubtle: '#FEF2F2',

  info: '#3B82F6',
  infoDark: '#2563EB',
  infoSubtle: '#EFF6FF',
} as const;

export const dark = {
  background: '#0F172A',
  paper:      '#1E293B',
  elevated:   '#263347',
  border:     'rgba(255,255,255,0.08)',
  textPrimary:   '#F1F5F9',
  textSecondary: '#94A3B8',
} as const;
