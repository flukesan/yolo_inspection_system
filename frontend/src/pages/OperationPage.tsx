import { useState, useRef, useEffect } from 'react';
import { Paper, Title, Stack, Group, Badge, Text, Button, Table, Alert, ActionIcon, Grid } from '@mantine/core';
import { IconCamera, IconRefresh } from '@tabler/icons-react';
import { snapAndInspect } from '../api/client';

interface SnapResult {
  result: string;
  confidence: number;
  defect_class: string | null;
  timestamp: string;
  snap_id: number;
}

export default function OperationPage() {
  const [snapping, setSnapping] = useState(false);
  const [lastResult, setLastResult] = useState<SnapResult | null>(null);
  const [history, setHistory] = useState<SnapResult[]>([]);
  const [error, setError] = useState('');
  const [wsConnected, setWsConnected] = useState(false);
  const [frameSrc, setFrameSrc] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket live camera — matches LiveCamera component pattern (base64 JSON frames)
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/ws/camera?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      setError('');
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'frame' && msg.data) {
          setFrameSrc(`data:image/jpeg;base64,${msg.data}`);
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

  const handleSnap = async () => {
    setSnapping(true);
    setError('');
    try {
      const res = await snapAndInspect();
      const result: SnapResult = res.data;
      setLastResult(result);
      setHistory((prev) => [result, ...prev].slice(0, 10));
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Snap failed — camera may be offline');
    } finally {
      setSnapping(false);
    }
  };

  const reconnectCamera = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setWsConnected(false);
    const token = localStorage.getItem('access_token');
    if (!token) return;
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/ws/camera?token=${token}`);
    ws.onopen = () => {
      setWsConnected(true);
      setError('');
    };
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'frame' && msg.data) {
          setFrameSrc(`data:image/jpeg;base64,${msg.data}`);
        } else if (msg.type === 'error') {
          setError(msg.message);
        }
      } catch {
        // ignore
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
    wsRef.current = ws;
  };

  return (
    <>
      <Group mb="md" justify="space-between">
        <Group>
          <Title order={3}>Operation</Title>
          <Badge size="lg" color={wsConnected ? 'green' : 'red'} variant="filled">
            {wsConnected ? '🟢 LIVE' : '🔴 OFFLINE'}
          </Badge>
        </Group>
        <ActionIcon variant="subtle" size="lg" onClick={reconnectCamera} title="Reconnect camera">
          <IconRefresh size={20} />
        </ActionIcon>
      </Group>

      {error && (
        <Alert color="red" variant="light" mb="md" onClose={() => setError('')} withCloseButton>
          {error}
        </Alert>
      )}

      <Grid>
        <Grid.Col span={{ base: 12, lg: 8 }}>
          {/* Live Camera View */}
          <Paper
            withBorder
            radius="md"
            style={{
              overflow: 'hidden',
              background: '#000',
              minHeight: 400,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
            }}
          >
            {wsConnected && frameSrc ? (
              <img
                src={frameSrc}
                alt="Live camera"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              />
            ) : (
              <Stack align="center" gap="xs">
                <IconCamera size={64} stroke={1} color="gray" />
                <Text c="dimmed">Camera offline</Text>
                <Button variant="light" size="sm" onClick={reconnectCamera}>
                  Reconnect
                </Button>
              </Stack>
            )}

            {/* Result overlay */}
            {lastResult && (
              <Paper
                style={{ position: 'absolute', top: 16, right: 16, minWidth: 180 }}
                p="md"
                radius="md"
                shadow="xl"
                bg={lastResult.result === 'OK' ? 'rgba(0,200,0,0.9)' : 'rgba(220,50,50,0.9)'}
              >
                <Stack gap={4} align="center">
                  <Text size="xl" fw={900} c="white">
                    {lastResult.result}
                  </Text>
                  <Text size="sm" c="white">
                    Confidence: {(lastResult.confidence * 100).toFixed(1)}%
                  </Text>
                  {lastResult.defect_class && (
                    <Badge color="yellow" variant="filled">
                      {lastResult.defect_class}
                    </Badge>
                  )}
                  <Text size="xs" c="white" opacity={0.8}>
                    {new Date(lastResult.timestamp).toLocaleTimeString()}
                  </Text>
                </Stack>
              </Paper>
            )}
          </Paper>

          {/* Snap Button */}
          <Group mt="md" justify="center">
            <Button
              size="xl"
              color="orange"
              leftSection={<IconCamera size={24} />}
              onClick={handleSnap}
              loading={snapping}
              disabled={!wsConnected}
              style={{ minWidth: 200, height: 56 }}
            >
              {snapping ? 'Inspecting...' : 'SNAP & INSPECT'}
            </Button>
          </Group>
        </Grid.Col>

        <Grid.Col span={{ base: 12, lg: 4 }}>
          {/* Recent Results */}
          <Paper withBorder p="md" radius="md">
            <Text fw={700} mb="xs">
              📋 Recent Inspections
            </Text>
            {history.length === 0 ? (
              <Text size="sm" c="dimmed" ta="center" py="xl">
                No inspections yet. Press SNAP to start.
              </Text>
            ) : (
              <Table striped highlightOnHover>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th>Result</Table.Th>
                    <Table.Th>Confidence</Table.Th>
                    <Table.Th>Defect</Table.Th>
                    <Table.Th>Time</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {history.map((h, i) => (
                    <Table.Tr key={h.snap_id || i}>
                      <Table.Td>
                        <Badge size="sm" color={h.result === 'OK' ? 'green' : 'red'} variant="filled">
                          {h.result}
                        </Badge>
                      </Table.Td>
                      <Table.Td>{(h.confidence * 100).toFixed(1)}%</Table.Td>
                      <Table.Td>{h.defect_class || '—'}</Table.Td>
                      <Table.Td style={{ fontSize: 12, color: '#888' }}>
                        {new Date(h.timestamp).toLocaleTimeString()}
                      </Table.Td>
                    </Table.Tr>
                  ))}
                </Table.Tbody>
              </Table>
            )}
          </Paper>
        </Grid.Col>
      </Grid>
    </>
  );
}
