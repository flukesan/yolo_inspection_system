import { useState, useEffect } from 'react';
import { Paper, Title, Table, Badge, Button, Group, TextInput, Select, ActionIcon, Tooltip, Text, Skeleton } from '@mantine/core';
import { IconSearch, IconDownload, IconEye } from '@tabler/icons-react';
import { getInspections } from '../api/client';
import type { InspectionQuery } from '../api/client';
import InspectionDetail from '../components/InspectionDetail';

interface Inspection { id: number; part_id: string; result: string; defect_class: string | null; station: string; confidence: number; timestamp: string; }

export default function HistoryPage() {
  const [inspections, setInspections] = useState<Inspection[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState<InspectionQuery>({ page: 1, limit: 20 });
  const [searchPartId, setSearchPartId] = useState('');
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  const fetchInspections = async () => {
    setLoading(true);
    try { const res = await getInspections({ ...filters, page, part_id: searchPartId || undefined }); setInspections(res.data.items || res.data || []); setTotalPages(res.data.total_pages || 1); }
    catch { setInspections([]); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchInspections(); }, [page, filters]);

  const handleSearch = () => { setPage(1); fetchInspections(); };

  const handleExportCSV = () => {
    const headers = ['ID', 'Part ID', 'Result', 'Defect Class', 'Station', 'Confidence', 'Timestamp'];
    const rows = inspections.map((i) => [i.id, i.part_id, i.result, i.defect_class || '', i.station, i.confidence, i.timestamp].join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inspections_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const openDetail = (id: number) => { setSelectedId(id); setDetailOpen(true); };

  return <>
    <Title order={3} mb="md">Inspection History</Title>
    <Paper withBorder p="md" radius="md" mb="md">
      <Group>
        <TextInput placeholder="Part ID..." value={searchPartId} onChange={(e) => setSearchPartId(e.currentTarget.value)} onKeyDown={(e) => e.key === 'Enter' && handleSearch()} leftSection={<IconSearch size={16} />} style={{ flex: 1 }} />
        <Select placeholder="Result" data={[{ value: '', label: 'All' }, { value: 'OK', label: 'OK' }, { value: 'NG', label: 'NG' }]} value={filters.result || ''} onChange={(v) => setFilters({ ...filters, result: v || undefined })} clearable />
        <Select placeholder="Station" data={[{ value: '', label: 'All' }, { value: 'Station-1', label: 'Station 1' }, { value: 'Station-2', label: 'Station 2' }, { value: 'Station-3', label: 'Station 3' }]} value={filters.station || ''} onChange={(v) => setFilters({ ...filters, station: v || undefined })} clearable />
        <Button color="orange" onClick={handleSearch}>Search</Button>
        <Tooltip label="Export CSV"><ActionIcon variant="light" color="green" size="lg" onClick={handleExportCSV}><IconDownload size={18} /></ActionIcon></Tooltip>
      </Group>
    </Paper>
    <Paper withBorder radius="md">
      <Table highlightOnHover>
        <Table.Thead><Table.Tr><Table.Th>ID</Table.Th><Table.Th>Part ID</Table.Th><Table.Th>Result</Table.Th><Table.Th>Defect</Table.Th><Table.Th>Station</Table.Th><Table.Th>Confidence</Table.Th><Table.Th>Timestamp</Table.Th><Table.Th></Table.Th></Table.Tr></Table.Thead>
        <Table.Tbody>
          {loading ? Array.from({ length: 5 }).map((_, i) => <Table.Tr key={i}>{Array.from({ length: 8 }).map((_, j) => <Table.Td key={j}><Skeleton h={20} /></Table.Td>)}</Table.Tr>)
          : inspections.map((row) => <Table.Tr key={row.id}>
            <Table.Td>{row.id}</Table.Td><Table.Td fw={500}>{row.part_id}</Table.Td>
            <Table.Td><Badge color={row.result === 'OK' ? 'green' : 'red'}>{row.result}</Badge></Table.Td>
            <Table.Td>{row.defect_class || '-'}</Table.Td><Table.Td>{row.station}</Table.Td>
            <Table.Td>{(row.confidence * 100).toFixed(1)}%</Table.Td>
            <Table.Td>{new Date(row.timestamp).toLocaleString()}</Table.Td>
            <Table.Td><ActionIcon variant="subtle" color="gray" onClick={() => openDetail(row.id)}><IconEye size={16} /></ActionIcon></Table.Td>
          </Table.Tr>)}
        </Table.Tbody>
      </Table>
      <Group justify="center" p="md">
        <Button variant="light" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>Previous</Button>
        <Text size="sm" c="dimmed">Page {page} of {totalPages}</Text>
        <Button variant="light" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</Button>
      </Group>
    </Paper>
    <InspectionDetail id={selectedId} opened={detailOpen} onClose={() => setDetailOpen(false)} />
  </>;
}
