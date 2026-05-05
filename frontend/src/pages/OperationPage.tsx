import { useState, useRef, useEffect } from 'react';
import { Paper, Stack, Group, Badge, Text, Button, Alert, ActionIcon, Table, Drawer } from '@mantine/core';
import { IconCamera, IconRefresh, IconArrowLeft, IconList, IconMaximize, IconMinimize } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
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
  const [historyOpen, setHistoryOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // ── Fullscreen API ────────────────────────────────────────────
  const enterFullscreen = async () => {
    try {
      await document.documentElement.requestFullscreen();
    } catch {}
  };
  const exitFullscreen = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
    } catch {}
  };
  const toggleFullscreen = () => (isFullscreen ? exitFullscreen() : enterFullscreen());

  useEffect(() => {
    const onFsChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener('fullscreenchange', onFsChange);
    // Auto-enter fullscreen when page mounts
    enterFullscreen();
    return () => document.removeEventListener('fullscreenchange', onFsChange);
  }, []);

  // WebSocket live camera
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/ws/camera?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => { setWsConnected(true); setError(''); };
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'frame' && msg.data) {
          setFrameSrc(`data:image/jpeg;base64,${msg.data}`);
        } else if (msg.type === 'error') {
          setError(msg.message);
        }
      } catch {}
    };
    ws.onclose = () => { setWsConnected(false); setFrameSrc(null); };
    ws.onerror = () => { setWsConnected(false); setError('Camera WebSocket error'); };

    return () => { ws.close(); wsRef.current = null; };
  }, []);

  const handleSnap = async () => {
    setSnapping(true);
    setError('');
    try {
      const res = await snapAndInspect();
      const result: SnapResult = res.data;
      setLastResult(result);
      setHistory((prev) => [result, ...prev].slice(0, 50));
      // Auto-clear result overlay after 4 seconds
      setTimeout(() => setLastResult(null), 4000);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Snap failed');
    } finally {
      setSnapping(false);
    }
  };

  const reconnectCamera = () => {
    if (wsRef.current) wsRef.current.close();
    setWsConnected(false);
    const token = localStorage.getItem('access_token');
    if (!token) return;
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/ws/camera?token=${token}`);
    ws.onopen = () => { setWsConnected(true); setError(''); };
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'frame' && msg.data) {
          setFrameSrc(`data:image/jpeg;base64,${msg.data}`);
        }
      } catch {}
    };
    ws.onclose = () => { setWsConnected(false); setFrameSrc(null); };
    ws.onerror = () => setWsConnected(false);
    wsRef.current = ws;
  };

  return (
    <div style={{ width: '100vw', height: '100vh', background: '#000', position: 'relative', overflow: 'hidden' }}>
      {/* ── Camera Background ──────────────────────────────────── */}
      {wsConnected && frameSrc ? (
        <img
          src={frameSrc}
          alt="Live camera"
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'contain',
            position: 'absolute',
            top: 0, left: 0,
          }}
        />
      ) : (
        <Stack
          align="center"
          justify="center"
          style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0 }}
        >
          <IconCamera size={80} stroke={1} color="#555" />
          <Text c="dimmed" size="lg">Camera offline</Text>
          <Button variant="light" size="md" onClick={reconnectCamera}>Reconnect</Button>
        </Stack>
      )}

      {/* ── Top Bar ─────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0,
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '8px 12px',
        background: 'rgba(0,0,0,0.6)',
        backdropFilter: 'blur(8px)',
        zIndex: 10,
      }}>
        <Group gap="xs">
          <ActionIcon variant="subtle" color="gray" onClick={() => { exitFullscreen(); setTimeout(() => navigate('/dashboard'), 100); }}>
            <IconArrowLeft size={20} />
          </ActionIcon>
          <Badge size="sm" color={wsConnected ? 'green' : 'red'} variant="filled">
            {wsConnected ? '🟢 LIVE' : '🔴 OFFLINE'}
          </Badge>
        </Group>
        <Group gap="xs">
          <ActionIcon variant="subtle" color="gray" onClick={toggleFullscreen} title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
            {isFullscreen ? <IconMinimize size={20} /> : <IconMaximize size={20} />}
          </ActionIcon>
          <ActionIcon variant="subtle" color="gray" onClick={() => setHistoryOpen(true)} title="History">
            <IconList size={20} />
          </ActionIcon>
          <ActionIcon variant="subtle" color="gray" onClick={reconnectCamera} title="Reconnect">
            <IconRefresh size={20} />
          </ActionIcon>
        </Group>
      </div>

      {/* ── Error Toast ─────────────────────────────────────────── */}
      {error && (
        <Alert
          color="red" variant="filled"
          style={{ position: 'absolute', top: 52, left: 12, right: 12, zIndex: 11 }}
          onClose={() => setError('')} withCloseButton
        >
          {error}
        </Alert>
      )}

      {/* ── Result Overlay ──────────────────────────────────────── */}
      {lastResult && (
        <Paper
          style={{
            position: 'absolute',
            top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            minWidth: 220,
            zIndex: 10,
            animation: 'fadeIn 0.3s ease',
          }}
          p="lg"
          radius="lg"
          shadow="xl"
          bg={lastResult.result === 'OK' ? 'rgba(0,180,0,0.92)' : 'rgba(220,40,40,0.92)'}
        >
          <Stack gap={4} align="center">
            <Text fz={40} fw={900} c="white" style={{ lineHeight: 1 }}>
              {lastResult.result}
            </Text>
            <Text size="md" c="white" opacity={0.9}>
              {(lastResult.confidence * 100).toFixed(1)}%
            </Text>
            {lastResult.defect_class && (
              <Badge size="lg" color="yellow" variant="filled">
                {lastResult.defect_class}
              </Badge>
            )}
          </Stack>
        </Paper>
      )}

      {/* ── Snap Button (bottom center) ─────────────────────────── */}
      <div style={{
        position: 'absolute', bottom: 24, left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 10,
      }}>
        <Button
          size="xl"
          color="orange"
          leftSection={<IconCamera size={28} />}
          onClick={handleSnap}
          loading={snapping}
          disabled={!wsConnected}
          style={{ minWidth: 240, height: 60, fontSize: 20, fontWeight: 700, borderRadius: 30 }}
        >
          {snapping ? 'INSPECTING...' : 'SNAP & INSPECT'}
        </Button>
      </div>

      {/* ── History Drawer ──────────────────────────────────────── */}
      <Drawer
        opened={historyOpen}
        onClose={() => setHistoryOpen(false)}
        title="📋 Inspection History"
        position="right"
        size="sm"
        padding="md"
        styles={{ content: { background: '#161B22' } }}
      >
        {history.length === 0 ? (
          <Text size="sm" c="dimmed" ta="center" py="xl">No inspections yet</Text>
        ) : (
          <Table striped highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Result</Table.Th>
                <Table.Th>Conf</Table.Th>
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
                  <Table.Td>{(h.confidence * 100).toFixed(0)}%</Table.Td>
                  <Table.Td>{h.defect_class || '—'}</Table.Td>
                  <Table.Td style={{ fontSize: 11, color: '#888' }}>
                    {new Date(h.timestamp).toLocaleTimeString()}
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
      </Drawer>

      {/* ── fadeIn animation ────────────────────────────────────── */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
          to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
      `}</style>
    </div>
  );
}
