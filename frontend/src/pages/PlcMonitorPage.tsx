import { useState, useEffect, useRef } from 'react';
import { Paper, Title, Stack, Group, Badge, Text, Grid, Table, Code, Alert } from '@mantine/core';
import { IconPlugConnected, IconPlugConnectedX } from '@tabler/icons-react';
import { getPlcStatus, getPlcData } from '../api/client';

export default function PlcMonitorPage() {
  const [connected, setConnected] = useState(false);
  const [mockMode, setMockMode] = useState(false);
  const [host, setHost] = useState('');
  const [data, setData] = useState<{
    m_bits: Record<string, boolean>;
    i_bits: Record<string, boolean>;
    q_bits: Record<string, boolean>;
    m_words: Record<string, number>;
    db_values: Record<string, unknown>;
    timestamp: number;
  } | null>(null);
  const [error, setError] = useState('');
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    loadData();
    intervalRef.current = setInterval(loadData, 1000);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, []);

  const loadData = async () => {
    try {
      const [statusRes, dataRes] = await Promise.all([getPlcStatus(), getPlcData()]);
      setConnected(statusRes.data.connected);
      setMockMode(statusRes.data.mock_mode);
      setHost(statusRes.data.host);
      setData(dataRes.data);
      setError('');
    } catch { setError('Failed to fetch PLC data'); }
  };

  const bitColor = (val: boolean) => val ? 'green' : 'red';

  const renderBitGrid = (bits: Record<string, boolean>, title: string) => {
    const keys = Object.keys(bits).sort();
    if (keys.length === 0) return <Text size="sm" c="dimmed">No data</Text>;
    const groups: Record<string, string[]> = {};
    keys.forEach(k => { const byte = k.split('.')[0]; if (!groups[byte]) groups[byte] = []; groups[byte].push(k); });
    return <Stack gap="xs"><Text fw={700} size="sm">{title}</Text>
      {Object.entries(groups).map(([byte, bits_]) => (
        <Group key={byte} gap={4}>
          <Text size="xs" c="dimmed" w={30}>{byte}</Text>
          {bits_.map(b => <Badge key={b} size="sm" color={bitColor(bits[b])} variant="filled" style={{minWidth:42}}>{b.split('.')[1]}:{bits[b]?'ON':'OFF'}</Badge>)}
        </Group>
      ))}
    </Stack>;
  };

  const renderWords = (words: Record<string, number>) => {
    const keys = Object.keys(words).sort();
    if (keys.length === 0) return <Text size="sm" c="dimmed">No data</Text>;
    return <Table striped highlightOnHover>
      <Table.Thead><Table.Tr><Table.Th>Address</Table.Th><Table.Th>Decimal</Table.Th><Table.Th>HEX</Table.Th><Table.Th>Binary</Table.Th></Table.Tr></Table.Thead>
      <Table.Tbody>{keys.map(k => {
        const v = words[k];
        return <Table.Tr key={k}><Table.Td><Code>{k}</Code></Table.Td><Table.Td>{v}</Table.Td><Table.Td>0x{v.toString(16).toUpperCase().padStart(4,'0')}</Table.Td><Table.Td style={{fontFamily:'monospace',fontSize:11}}>{v.toString(2).padStart(16,'0')}</Table.Td></Table.Tr>;
      })}</Table.Tbody>
    </Table>;
  };

  const renderDb = (db: Record<string, unknown>) => {
    const keys = Object.keys(db).sort();
    if (keys.length === 0) return <Text size="sm" c="dimmed">No data</Text>;
    return <Table striped highlightOnHover>
      <Table.Thead><Table.Tr><Table.Th>Address</Table.Th><Table.Th>Value</Table.Th><Table.Th>Type</Table.Th></Table.Tr></Table.Thead>
      <Table.Tbody>{keys.map(k => {
        const v = db[k];
        const type = typeof v === 'boolean' ? 'BOOL' : typeof v === 'number' ? (Number.isInteger(v)?'INT':'REAL') : typeof v;
        const display = typeof v === 'boolean' ? (v?'TRUE':'FALSE') : typeof v === 'number' ? (Number.isInteger(v)?v.toString():(v as number).toFixed(4)) : String(v);
        return <Table.Tr key={k}><Table.Td><Code>{k}</Code></Table.Td><Table.Td fw={500}>{display}</Table.Td><Table.Td><Badge size="xs" color="gray" variant="light">{type}</Badge></Table.Td></Table.Tr>;
      })}</Table.Tbody>
    </Table>;
  };

  return <>
    <Group mb="md">
      <Title order={3}>PLC Monitor</Title>
      <Badge size="lg" color={connected?'green':'red'} leftSection={connected?<IconPlugConnected size={14}/>:<IconPlugConnectedX size={14}/>}>{connected?'LIVE':'DISCONNECTED'}</Badge>
      {mockMode&&<Badge size="lg" color="yellow" variant="filled">MOCK</Badge>}
      <Text size="sm" c="dimmed">PLC: {host||'—'}</Text>
    </Group>
    {error&&<Alert color="red" variant="light" mb="md">{error}</Alert>}
    {data ? <Grid>
      <Grid.Col span={12}>
        <Paper withBorder p="md" radius="md" mb="md">
          <Grid>
            <Grid.Col span={4}>{renderBitGrid(data.m_bits, '📥 M (Memory) Bits')}</Grid.Col>
            <Grid.Col span={4}>{renderBitGrid(data.i_bits, '📥 I (Input) Bits')}</Grid.Col>
            <Grid.Col span={4}>{renderBitGrid(data.q_bits, '📤 Q (Output) Bits')}</Grid.Col>
          </Grid>
        </Paper>
      </Grid.Col>
      <Grid.Col span={6}>
        <Paper withBorder p="md" radius="md"><Text fw={700} size="sm" mb="xs">📊 M (Memory) Words</Text>{renderWords(data.m_words)}</Paper>
      </Grid.Col>
      <Grid.Col span={6}>
        <Paper withBorder p="md" radius="md"><Text fw={700} size="sm" mb="xs">🗄️ DB (Data Block) Values</Text>{renderDb(data.db_values)}</Paper>
      </Grid.Col>
      <Grid.Col span={12}><Text size="xs" c="dimmed" ta="right">Last update: {new Date(data.timestamp*1000).toLocaleTimeString()}</Text></Grid.Col>
    </Grid> : <Paper withBorder p="xl" radius="md"><Text c="dimmed" ta="center">Loading PLC data...</Text></Paper>}
  </>;
}
