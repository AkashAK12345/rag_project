// src/store/authStore.ts
import { createContext, useContext } from 'react';
import type { UserResponse } from '@/types/auth';

export interface AuthState {
  user: UserResponse | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: UserResponse) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);

export const useAuthContext = (): AuthState => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
};
