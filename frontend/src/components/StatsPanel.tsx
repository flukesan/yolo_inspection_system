import { useState, useEffect } from 'react';
import { Paper, SimpleGrid, RingProgress, Text, Group, Skeleton } from '@mantine/core';
import { IconCheck, IconX } from '@tabler/icons-react';
import { getStats } from '../api/client';

interface StatsData { total: number; ok: number; ng: number; rate: number; period_hours: number; }

export default function StatsPanel() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchStats = async () => {
    try { setError(false); const res = await getStats(); setStats(res.data); }
    catch { setError(true); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchStats(); const interval = setInterval(fetchStats, 5000); return () => clearInterval(interval); }, []);

  if (loading) return <SimpleGrid cols={{ base: 1, sm: 3 }}><Skeleton h={160} radius="md" /><Skeleton h={160} radius="md" /><Skeleton h={160} radius="md" /></SimpleGrid>;

  const displayOk = error ? 0 : stats?.ok || 0;
  const displayNg = error ? 0 : stats?.ng || 0;
  const displayRate = error ? 0 : stats?.rate || 0;

  return (
    <SimpleGrid cols={{ base: 1, sm: 3 }}>
      <Paper withBorder p="lg" radius="md" ta="center">
        <RingProgress size={140} thickness={12} roundCaps
          sections={[{ value: displayRate, color: displayRate >= 95 ? 'green' : displayRate >= 80 ? 'yellow' : 'red' }]}
          label={<Text size="xl" fw={700} ta="center">{displayRate.toFixed(1)}%</Text>} mx="auto" />
        <Text size="sm" c="dimmed" mt="sm">OK Rate (last {stats?.period_hours || 24}h)</Text>
      </Paper>
      <Paper withBorder p="lg" radius="md">
        <Group justify="space-between" mb="xs">
          <IconCheck size={32} color="var(--mantine-color-green-6)" /><Text size="xs" c="dimmed">PASS</Text>
        </Group>
        <Text size="32px" fw={700} c="green.6">{displayOk.toLocaleString()}</Text>
        <Text size="sm" c="dimmed">OK Inspections</Text>
      </Paper>
      <Paper withBorder p="lg" radius="md">
        <Group justify="space-between" mb="xs">
          <IconX size={32} color="var(--mantine-color-red-6)" /><Text size="xs" c="dimmed">FAIL</Text>
        </Group>
        <Text size="32px" fw={700} c="red.6">{displayNg.toLocaleString()}</Text>
        <Text size="sm" c="dimmed">NG Inspections</Text>
      </Paper>
    </SimpleGrid>
  );
}
