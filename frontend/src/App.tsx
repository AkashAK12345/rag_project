// src/App.tsx
import { useState, useMemo, type ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, CssBaseline, type PaletteMode } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { SnackbarProvider } from 'notistack';
import { createAppTheme } from '@/theme';
import { ThemeContext } from '@/store/themeStore';
import { AuthProvider } from '@/features/auth/AuthProvider';
import { AppRouter } from '@/routes/AppRouter';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  const [mode, setMode] = useState<PaletteMode>(() => {
    const saved = localStorage.getItem('theme_mode');
    return saved === 'dark' ? 'dark' : 'light';
  });

  const toggleTheme = () =>
    setMode((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme_mode', next);
      return next;
    });

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const themeValue = useMemo(() => ({ mode, toggleTheme }), [mode]);

  return (
    <ThemeContext.Provider value={themeValue}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline />
        <SnackbarProvider
          maxSnack={4}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          autoHideDuration={4000}
        >
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              <AppRouter />
            </AuthProvider>
            <ReactQueryDevtools initialIsOpen={false} />
          </QueryClientProvider>
        </SnackbarProvider>
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}

// Suppress unused ReactNode warning
void (null as unknown as ReactNode);
