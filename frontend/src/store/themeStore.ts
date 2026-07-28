// src/store/themeStore.ts
import { createContext, useContext } from 'react';
import type { PaletteMode } from '@mui/material';

export interface ThemeState {
  mode: PaletteMode;
  toggleTheme: () => void;
}

export const ThemeContext = createContext<ThemeState | null>(null);

export const useThemeContext = (): ThemeState => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useThemeContext must be used within ThemeProvider');
  return ctx;
};
