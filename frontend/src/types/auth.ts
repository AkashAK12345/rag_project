// src/types/auth.ts
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
}

export type UserRole = 'ADMIN' | 'MANAGER' | 'ANALYST' | 'VIEWER';
