// src/api/authApi.ts
import { axiosClient } from './axiosClient';
import type { LoginRequest, TokenResponse, UserResponse } from '@/types/auth';

export const authApi = {
  login: async (body: LoginRequest): Promise<TokenResponse> => {
    const { data } = await axiosClient.post<TokenResponse>('/auth/login', body);
    return data;
  },

  me: async (): Promise<UserResponse> => {
    const { data } = await axiosClient.get<UserResponse>('/auth/me');
    return data;
  },

  logout: async (): Promise<void> => {
    await axiosClient.post('/auth/logout');
  },
};
