import { useState, useEffect, useRef } from 'react';
import { Paper, Title, Stack, Group, Badge, Text, Grid, Table, Code, Alert, TextInput, Button, ActionIcon } from '@mantine/core';
import { IconPlugConnected, IconPlugConnectedX, IconPlus, IconTrash } from '@tabler/icons-react';
import { getPlcStatus, getPlcData, getPlcAddresses, setPlcAddresses } from '../api/client';

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

  const [watchAddrs, setWatchAddrs] = useState<string[]>([]);
  const [watchValues, setWatchValues] = useState<Record<string, {value:unknown, type:string}>>({});
  const [newAddr, setNewAddr] = useState('');
  const [addrError, setAddrError] = useState('');

  useEffect(() => {
    loadData();
    loadAddresses();
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
      if (watchAddrs.length > 0) {
        const vals: Record<string, {value:unknown, type:string}> = {};
        for (const addr of watchAddrs) {
          const v = resolveAddr(dataRes.data, addr);
          vals[addr] = { value: v, type: typeof v };
        }
        setWatchValues(vals);
      }
    } catch { setError('Failed to fetch PLC data'); }
  };

  const loadAddresses = async () => {
    try { const res = await getPlcAddresses(); setWatchAddrs(res.data.addresses || []); } catch {}
  };

  const resolveAddr = (d: typeof data, addr: string): unknown => {
    if (!d) return null;
    if (addr.startsWith('M') && addr.includes('.')) return d.m_bits?.[addr] ?? false;
    if (addr.startsWith('I') && addr.includes('.')) return d.i_bits?.[addr] ?? false;
    if (addr.startsWith('Q') && addr.includes('.')) return d.q_bits?.[addr] ?? false;
    if (addr.startsWith('MW')) return d.m_words?.[addr] ?? 0;
    if (addr.startsWith('DB')) return d.db_values?.[addr] ?? 0;
    return null;
  };

  const addAddress = async () => {
    const addr = newAddr.trim().toUpperCase();
    if (!addr) return;
    if (!/^(M|I|Q)\d+\.\d+$|^MW\d+$|^DB\d+\.(DBD|DBW|DBX)\d+(\.\d+)?$/i.test(addr)) {
      setAddrError('Invalid format. Use: M0.0, I0.0, Q0.0, MW2, DB1.DBD4, DB1.DBX10.0');
      return;
    }
    if (watchAddrs.includes(addr)) { setAddrError('Address already in list'); return; }
    setAddrError('');
    const newList = [...watchAddrs, addr];
    setWatchAddrs(newList); setNewAddr('');
    try { await setPlcAddresses(newList); } catch {}
  };

  const removeAddress = async (addr: string) => {
    const newList = watchAddrs.filter(a => a !== addr);
    setWatchAddrs(newList);
    try { await setPlcAddresses(newList); } catch {}
  };

  const bitColor = (val: boolean) => val ? 'green' : 'red';

  const renderBitGrid = (bits: Record<string, boolean>, title: string) => {
    const keys = Object.keys(bits).sort();
    if (keys.length === 0) return <Text size="sm" c="dimmed">No data</Text>;
    const groups: Record<string, string[]> = {};
    keys.forEach(k => { const byte = k.split('.')[0]; if (!groups[byte]) groups[byte] = []; groups[byte].push(k); });
    return <Stack gap="xs"><Text fw={700} size="sm">{title}</Text>
      {Object.entries(groups).map(([byte, bits_]) => (
        <Group key={byte} gap={4}><Text size="xs" c="dimmed" w={30}>{byte}</Text>
          {bits_.map(b => <Badge key={b} size="sm" color={bitColor(bits[b])} variant="filled" style={{minWidth:42}}>{b.split('.')[1]}:{bits[b]?'ON':'OFF'}</Badge>)}
        </Group>
      ))}</Stack>;
  };

  const renderWords = (words: Record<string, number>) => {
    const keys = Object.keys(words).sort();
    if (keys.length === 0) return <Text size="sm" c="dimmed">No data</Text>;
    return <Table striped highlightOnHover><Table.Thead><Table.Tr><Table.Th>Address</Table.Th><Table.Th>Decimal</Table.Th><Table.Th>HEX</Table.Th><Table.Th>Binary</Table.Th></Table.Tr></Table.Thead>
      <Table.Tbody>{keys.map(k => { const v = words[k];
        return <Table.Tr key={k}><Table.Td><Code>{k}</Code></Table.Td><Table.Td>{v}</Table.Td><Table.Td>0x{v.toString(16).toUpperCase().padStart(4,'0')}</Table.Td><Table.Td style={{fontFamily:'monospace',fontSize:11}}>{v.toString(2).padStart(16,'0')}</Table.Td></Table.Tr>;
    })}</Table.Tbody></Table>;
  };

  const renderDb = (db: Record<string, unknown>) => {
    const keys = Object.keys(db).sort();
    if (keys.length === 0) return <Text size="sm" c="dimmed">No data</Text>;
    return <Table striped highlightOnHover><Table.Thead><Table.Tr><Table.Th>Address</Table.Th><Table.Th>Value</Table.Th><Table.Th>Type</Table.Th></Table.Tr></Table.Thead>
      <Table.Tbody>{keys.map(k => { const v = db[k];
        const type = typeof v === 'boolean' ? 'BOOL' : typeof v === 'number' ? (Number.isInteger(v)?'INT':'REAL') : typeof v;
        const display = typeof v === 'boolean' ? (v?'TRUE':'FALSE') : typeof v === 'number' ? (Number.isInteger(v)?v.toString():(v as number).toFixed(4)) : String(v);
        return <Table.Tr key={k}><Table.Td><Code>{k}</Code></Table.Td><Table.Td fw={500}>{display}</Table.Td><Table.Td><Badge size="xs" color="gray" variant="light">{type}</Badge></Table.Td></Table.Tr>;
    })}</Table.Tbody></Table>;
  };

  const renderWatchTable = () => {
    if (watchAddrs.length === 0) return <Text size="sm" c="dimmed" ta="center" py="md">No custom addresses. Add one below.</Text>;
    return <Table striped highlightOnHover>
      <Table.Thead><Table.Tr><Table.Th>Address</Table.Th><Table.Th>Value</Table.Th><Table.Th>Type</Table.Th><Table.Th></Table.Th></Table.Tr></Table.Thead>
      <Table.Tbody>{watchAddrs.map(addr => {
        const v = watchValues[addr];
        const display = v ? (typeof v.value === 'boolean' ? (v.value ? '✅ ON' : '⬛ OFF') : String(v.value)) : '—';
        const color = v && typeof v.value === 'boolean' ? (v.value ? 'green' : 'red') : undefined;
        return <Table.Tr key={addr}>
          <Table.Td><Code>{addr}</Code></Table.Td>
          <Table.Td><Text c={color} fw={500}>{display}</Text></Table.Td>
          <Table.Td><Badge size="xs" color="gray" variant="light">{v?.type || '—'}</Badge></Table.Td>
          <Table.Td><ActionIcon size="sm" color="red" variant="subtle" onClick={() => removeAddress(addr)}><IconTrash size={14}/></ActionIcon></Table.Td>
        </Table.Tr>;
    })}</Table.Tbody></Table>;
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
      <Grid.Col span={12}><Paper withBorder p="md" radius="md" mb="md"><Grid>
        <Grid.Col span={4}>{renderBitGrid(data.m_bits, '📥 M (Memory) Bits')}</Grid.Col>
        <Grid.Col span={4}>{renderBitGrid(data.i_bits, '📥 I (Input) Bits')}</Grid.Col>
        <Grid.Col span={4}>{renderBitGrid(data.q_bits, '📤 Q (Output) Bits')}</Grid.Col>
      </Grid></Paper></Grid.Col>
      <Grid.Col span={6}><Paper withBorder p="md" radius="md"><Text fw={700} size="sm" mb="xs">📊 M (Memory) Words</Text>{renderWords(data.m_words)}</Paper></Grid.Col>
      <Grid.Col span={6}><Paper withBorder p="md" radius="md"><Text fw={700} size="sm" mb="xs">🗄️ DB (Data Block) Values</Text>{renderDb(data.db_values)}</Paper></Grid.Col>
      <Grid.Col span={12}>
        <Paper withBorder p="md" radius="md">
          <Group mb="xs"><Text fw={700} size="sm">🔍 Custom Watch Addresses</Text><Badge size="sm" color="orange" variant="light">{watchAddrs.length} watched</Badge></Group>
          {renderWatchTable()}
          <Group mt="sm" align="flex-start">
            <TextInput placeholder="e.g. MW10, DB1.DBD4, M2.3" value={newAddr} onChange={(e) => { setNewAddr(e.currentTarget.value); setAddrError(''); }} onKeyDown={(e) => { if (e.key === 'Enter') addAddress(); }} error={addrError} style={{ flex: 1 }}/>
            <Button leftSection={<IconPlus size={14}/>} onClick={addAddress} color="orange">Add</Button>
          </Group>
          <Text size="xs" c="dimmed" mt={4}>Formats: M0.0, I0.0, Q0.0 (bits) | MW2 (word) | DB1.DBD4, DB1.DBX10.0 (data block)</Text>
        </Paper>
      </Grid.Col>
      <Grid.Col span={12}><Text size="xs" c="dimmed" ta="right">Last update: {new Date(data.timestamp*1000).toLocaleTimeString()}</Text></Grid.Col>
    </Grid> : <Paper withBorder p="xl" radius="md"><Text c="dimmed" ta="center">Loading PLC data...</Text></Paper>}
  </>;
}
