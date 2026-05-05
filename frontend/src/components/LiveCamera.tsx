import { useState, useEffect } from 'react';
import { Paper, Title, Badge, Stack, Text } from '@mantine/core';
import { IconCamera, IconPlugConnected, IconPlugConnectedX } from '@tabler/icons-react';

export default function LiveCamera() {
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/ws/camera?token=${token}`);
    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => setWsConnected(false);
    ws.onerror = () => setWsConnected(false);
    return () => ws.close();
  }, []);

  return (
    <Paper withBorder p="md" radius="md" h={420} style={{ position: 'relative', overflow: 'hidden' }}>
      <Stack align="center" justify="center" h="100%">
        <IconCamera size={64} stroke={1.5} color="var(--mantine-color-dimmed)" />
        <Title order={4} c="dimmed">Camera Feed</Title>
        <Badge size="lg" color={wsConnected ? 'green' : 'red'}
          leftSection={wsConnected ? <IconPlugConnected size={14} /> : <IconPlugConnectedX size={14} />}>
          {wsConnected ? 'Live' : 'Disconnected'}
        </Badge>
        <Text size="xs" c="dimmed">
          {wsConnected ? 'Real-time inspection camera stream active' : 'Camera WebSocket not connected — check backend'}
        </Text>
      </Stack>
    </Paper>
  );
}
