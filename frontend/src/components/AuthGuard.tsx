import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated } from '../api/client';

let refreshTimer: ReturnType<typeof setInterval> | null = null;

function startTokenRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return;
    try {
      const { default: api } = await import('../api/client');
      const res = await api.post('/api/auth/refresh', { refresh_token: refresh });
      localStorage.setItem('access_token', res.data.access_token);
      if (res.data.refresh_token) localStorage.setItem('refresh_token', res.data.refresh_token);
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
  }, 25 * 60 * 1000);
}

interface AuthGuardProps { children: React.ReactNode; }

export default function AuthGuard({ children }: AuthGuardProps) {
  const navigate = useNavigate();
  useEffect(() => {
    if (!isAuthenticated()) { navigate('/login', { replace: true }); }
    else { startTokenRefresh(); }
  }, [navigate]);
  if (!isAuthenticated()) return null;
  return <>{children}</>;
}
