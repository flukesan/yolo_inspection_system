import { useState, useEffect, useRef } from 'react';
import { Paper, Title, Badge, Stack, Text, Image as MantineImage } from '@mantine/core';
import { IconCamera, IconPlugConnected, IconPlugConnectedX } from '@tabler/icons-react';

interface CameraInfo {
  source: string;
  type: string;
  configured: string;
  actual: string;
  connected: boolean;
}

export default function LiveCamera() {
  const [wsConnected, setWsConnected] = useState(false);
  const [frameSrc, setFrameSrc] = useState<string | null>(null);
  const [cameraInfo, setCameraInfo] = useState<CameraInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/ws/camera?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === 'frame' && msg.data) {
          setFrameSrc(`data:image/jpeg;base64,${msg.data}`);
        } else if (msg.type === 'status') {
          setCameraInfo(msg.info);
        } else if (msg.type === 'error') {
          setError(msg.message);
        }
      } catch {
        // ignore malformed messages
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      setFrameSrc(null);
    };

    ws.onerror = () => {
      setWsConnected(false);
      setError('Camera WebSocket error — check backend');
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, []);

  return (
    <Paper withBorder p="md" radius="md" h={420} style={{ position: 'relative', overflow: 'hidden' }}>
      {frameSrc ? (
        // ── Live frame ──────────────────────────────────────
        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
          <MantineImage
            src={frameSrc}
            alt="Camera Feed"
            fit="contain"
            h="100%"
            style={{ borderRadius: 4 }}
          />
          {/* Status overlay */}
          <div style={{
            position: 'absolute', top: 8, right: 8,
            display: 'flex', gap: 6,
          }}>
            <Badge size="sm" color={wsConnected ? 'green' : 'red'}
              leftSection={wsConnected ? <IconPlugConnected size={12} /> : <IconPlugConnectedX size={12} />}>
              {wsConnected ? 'LIVE' : 'RECONNECTING'}
            </Badge>
            {cameraInfo && (
              <Badge size="sm" color="dark" variant="light">
                {cameraInfo.actual}
              </Badge>
            )}
          </div>
        </div>
      ) : (
        // ── Placeholder ─────────────────────────────────────
        <Stack align="center" justify="center" h="100%">
          <IconCamera size={64} stroke={1.5} color="var(--mantine-color-dimmed)" />
          <Title order={4} c="dimmed">Camera Feed</Title>
          <Badge size="lg" color={wsConnected ? 'green' : 'red'}
            leftSection={wsConnected ? <IconPlugConnected size={14} /> : <IconPlugConnectedX size={14} />}>
            {wsConnected ? 'Live' : 'Disconnected'}
          </Badge>
          <Text size="xs" c="dimmed">
            {error || (wsConnected
              ? 'Waiting for camera frames...'
              : 'Camera WebSocket not connected — check backend')}
          </Text>
        </Stack>
      )}
    </Paper>
  );
}
