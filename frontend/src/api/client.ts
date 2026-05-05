import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const login = (username: string, password: string) =>
  api.post('/api/auth/login', { username, password });

export const refreshToken = () =>
  api.post('/api/auth/refresh', { refresh_token: localStorage.getItem('refresh_token') });

export const getMe = () => api.get('/api/auth/me');

export interface InspectionQuery {
  page?: number;
  limit?: number;
  result?: string;
  station?: string;
  from?: string;
  to?: string;
  part_id?: string;
}

export const createInspection = (data: Record<string, unknown>) =>
  api.post('/api/inspection', data);

export const getInspections = (params: InspectionQuery) =>
  api.get('/api/inspections', { params });

export const getInspectionById = (id: number) => api.get(`/api/inspection/${id}`);

export const getStats = () => api.get('/api/stats');
export const getStatsTrend = () => api.get('/api/stats/trend');

export const getPlcStatus = () => api.get('/api/plc/status');

export const getHealth = () => api.get('/api/health');

export const uploadImage = (formData: FormData) =>
  api.post('/api/images/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });

export const getImageUrl = (id: number) => api.get(`/api/images/${id}/url`);

export const setAuth = (access: string, refresh: string, user: unknown) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
  localStorage.setItem('user', JSON.stringify(user));
};

export const clearAuth = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

export const getUser = () => {
  try { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; }
  catch { return null; }
};

export const isAuthenticated = (): boolean => !!localStorage.getItem('access_token');

export const isEngineer = (): boolean => { const user = getUser(); return user?.role === 'engineer'; };

// Camera API
export const getCameraConfig = () => api.get('/api/camera/config');
export const updateCameraConfig = (data: Record<string, unknown>) => api.put('/api/camera/config', data);
export const restartCamera = () => api.post('/api/camera/restart');
export const getCameraSnapshot = () => api.get('/api/camera/snapshot');

export default api;
