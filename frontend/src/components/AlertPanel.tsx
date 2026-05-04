import { useState, useEffect } from 'react';
import { Notification, rem } from '@mantine/core';
import { IconX, IconAlertTriangle } from '@tabler/icons-react';

interface Alert { id: number; message: string; type: 'ng' | 'error'; timestamp: number; }
let nextId = 0;

export default function AlertPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const ws = new WebSocket(`ws://localhost:8000/api/ws/live?token=${token}`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.result === 'NG' || data.type === 'alert') {
          const alert: Alert = {
            id: nextId++,
            message: data.result === 'NG' ? `NG detected — ${data.defect_class || 'Unknown defect'}` : data.message || 'System alert',
            type: data.result === 'NG' ? 'ng' : 'error',
            timestamp: Date.now(),
          };
          setAlerts((prev) => [alert, ...prev].slice(0, 5));
        }
      } catch { /* ignore */ }
    };
    return () => ws.close();
  }, []);

  if (alerts.length === 0) return null;
  return <>{alerts.map((alert) => (
    <Notification key={alert.id}
      icon={alert.type === 'ng' ? <IconX size={rem(20)} /> : <IconAlertTriangle size={rem(20)} />}
      color={alert.type === 'ng' ? 'red' : 'yellow'}
      title={alert.type === 'ng' ? 'NG DEFECT DETECTED' : 'SYSTEM ALERT'} mt="md"
      onClose={() => setAlerts((prev) => prev.filter((a) => a.id !== alert.id))}>
      {alert.message}
    </Notification>
  ))}</>;
}
