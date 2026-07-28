// src/features/auth/AuthProvider.tsx
import { useState, useCallback, type ReactNode } from 'react';
import { AuthContext, type AuthState } from '@/store/authStore';
import type { UserResponse } from '@/types/auth';

interface Props { children: ReactNode }

export function AuthProvider({ children }: Props) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem('access_token'),
  );
  const [user, setUser] = useState<UserResponse | null>(() => {
    try {
      const raw = localStorage.getItem('user');
      return raw ? (JSON.parse(raw) as UserResponse) : null;
    } catch {
      return null;
    }
  });

  const login = useCallback((newToken: string, newUser: UserResponse) => {
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  }, []);

  const value: AuthState = {
    user,
    token,
    isAuthenticated: Boolean(token && user),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
