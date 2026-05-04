import { useState, useEffect } from 'react';
import { Paper, Badge, Text, Group, Stack } from '@mantine/core';
import { IconDatabase, IconServer, IconCloud } from '@tabler/icons-react';
import { getHealth } from '../api/client';

interface ServiceStatus { postgres: boolean; redis: boolean; minio: boolean; }

export default function SystemHealth() {
  const [health, setHealth] = useState<ServiceStatus | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchHealth = async () => { try { setError(false); const res = await getHealth(); setHealth({ postgres: res.data.postgres === 'healthy', redis: res.data.redis === 'healthy', minio: res.data.minio === 'healthy' }); } catch { setError(true); } };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const services: { key: keyof ServiceStatus; label: string; icon: React.ReactNode }[] = [
    { key: 'postgres', label: 'PostgreSQL', icon: <IconDatabase size={16} /> },
    { key: 'redis', label: 'Redis', icon: <IconServer size={16} /> },
    { key: 'minio', label: 'MinIO', icon: <IconCloud size={16} /> },
  ];

  return (
    <Paper withBorder p="md" radius="md">
      <Text size="sm" fw={500} c="dimmed" mb="sm">System Health</Text>
      <Stack gap="xs">
        {services.map(({ key, label, icon }) => (
          <Group key={key} justify="space-between">
            <Group gap="xs">{icon}<Text size="sm">{label}</Text></Group>
            <Badge color={error ? 'red' : health?.[key] ? 'green' : 'red'} variant="light">{error ? 'UNKNOWN' : health?.[key] ? 'Healthy' : 'Down'}</Badge>
          </Group>
        ))}
      </Stack>
    </Paper>
  );
}
