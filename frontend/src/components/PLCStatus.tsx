import { useState, useEffect } from 'react';
import { Paper, Badge, Text, Group, Stack } from '@mantine/core';
import { IconHeartbeat, IconPlugConnected, IconPlugConnectedX } from '@tabler/icons-react';
import { getPlcStatus } from '../api/client';

interface PlcStatusData { connected: boolean; heartbeat_ok: boolean; state: string; uptime: number; last_error: string | null; }

export default function PLCStatus() {
  const [status, setStatus] = useState<PlcStatusData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => { try { setError(false); const res = await getPlcStatus(); setStatus(res.data); } catch { setError(true); } };
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const connected = !error && status?.connected;
  const heartbeatOk = !error && status?.heartbeat_ok;
  const formatUptime = (s: number) => { const h = Math.floor(s / 3600); const m = Math.floor((s % 3600) / 60); return `${h}h ${m}m ${s % 60}s`; };

  return (
    <Paper withBorder p="md" radius="md">
      <Group justify="space-between" mb="sm">
        <Text size="sm" fw={500} c="dimmed">PLC Status</Text>
        <Badge color={connected ? 'green' : 'red'} leftSection={connected ? <IconPlugConnected size={14} /> : <IconPlugConnectedX size={14} />}>{connected ? 'Connected' : 'Disconnected'}</Badge>
      </Group>
      <Stack gap="xs">
        <Group justify="space-between"><Text size="sm" c="dimmed">Heartbeat</Text><Badge color={heartbeatOk ? 'green' : 'red'} variant="light" leftSection={<IconHeartbeat size={12} />}>{heartbeatOk ? 'OK' : 'MISSING'}</Badge></Group>
        <Group justify="space-between"><Text size="sm" c="dimmed">State</Text><Text size="sm" fw={500}>{status?.state || (error ? 'UNKNOWN' : '...')}</Text></Group>
        <Group justify="space-between"><Text size="sm" c="dimmed">Uptime</Text><Text size="sm" fw={500}>{status?.uptime ? formatUptime(status.uptime) : '-'}</Text></Group>
        {status?.last_error && <Group justify="space-between"><Text size="sm" c="red.4">Last Error</Text><Text size="sm" c="red.4">{status.last_error}</Text></Group>}
      </Stack>
    </Paper>
  );
}
