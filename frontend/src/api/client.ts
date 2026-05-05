import axios from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
const api = axios.create({baseURL:API_BASE,timeout:10000,headers:{'Content-Type':'application/json'}});
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use((r)=>r,(e)=>{
  if(e.response?.status===401){localStorage.clear();if(window.location.pathname!=='/login')window.location.href='/login';}
  return Promise.reject(e);
});

export const login = (u:string,p:string)=>api.post('/api/auth/login',{username:u,password:p});
export const getMe = ()=>api.get('/api/auth/me');
export const getStats = ()=>api.get('/api/stats');
export const getStatsTrend = ()=>api.get('/api/stats/trend');
export const getHealth = ()=>api.get('/api/health');

export const setAuth = (a:string,r:string,u:unknown)=>{localStorage.setItem('access_token',a);localStorage.setItem('refresh_token',r);localStorage.setItem('user',JSON.stringify(u));};
export const clearAuth = ()=>localStorage.clear();
export const getUser = ()=>{try{const u=localStorage.getItem('user');return u?JSON.parse(u):null}catch{return null}};
export const isAuthenticated = ():boolean=>!!localStorage.getItem('access_token');
export const isEngineer = ():boolean=>getUser()?.role==='engineer';

export const getCameraConfig = ()=>api.get('/api/camera/config');
export const updateCameraConfig = (d:Record<string,unknown>)=>api.put('/api/camera/config',d);
export const restartCamera = ()=>api.post('/api/camera/restart');
export const getCameraSnapshot = ()=>api.get('/api/camera/snapshot');

export const testPlcConnection = ()=>api.post('/api/plc/test');
export const getPlcStatus = ()=>api.get('/api/plc/status');
export const getPlcData = ()=>api.get('/api/plc/data');
export const getPlcAddresses = ()=>api.get('/api/plc/addresses');
export const setPlcAddresses = (a:string[])=>api.put('/api/plc/addresses',a);
export const readPlcAddress = (a:string)=>api.get('/api/plc/read',{params:{address:a}});
export const writePlcData = (d:Record<string,unknown>)=>api.post('/api/plc/write',d);

// Camera API
export const getCameraConfig = () => api.get('/api/camera/config');
export const updateCameraConfig = (data: Record<string, unknown>) => api.put('/api/camera/config', data);
export const restartCamera = () => api.post('/api/camera/restart');
export const getCameraSnapshot = () => api.get('/api/camera/snapshot');

// PLC API
export const testPlcConnection = () => api.post('/api/plc/test');
export const getPlcStatus = () => api.get('/api/plc/status');
export const getPlcData = () => api.get('/api/plc/data');
export const getPlcAddresses = () => api.get('/api/plc/addresses');
export const setPlcAddresses = (addrs: string[]) => api.put('/api/plc/addresses', addrs);
export const readPlcAddress = (address: string) => api.get('/api/plc/read', { params: { address } });
export const writePlcData = (data: Record<string, unknown>) => api.post('/api/plc/write', data);
export const getPlcConfig = () => api.get('/api/plc/config');
export const updatePlcConfig = (cfg: { host: string; rack: number; slot: number }) => api.put('/api/plc/config', cfg);

export default api;
