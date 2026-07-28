// src/api/axiosClient.ts
import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';

const BASE_URL = '/api/v1';

export const axiosClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120_000,
});

// ── Request interceptor: attach JWT ─────────────────────────────────────────
axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ── Response interceptor: handle 401 globally ───────────────────────────────
axiosClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      // Use replace so the user can't navigate back to a protected page
      window.location.replace('/login');
    }
    return Promise.reject(error);
  },
);
