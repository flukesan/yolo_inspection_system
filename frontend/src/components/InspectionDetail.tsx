import { useState, useEffect } from 'react';
import { Modal, Text, Badge, Stack, Image, Skeleton, Paper, Title, SimpleGrid } from '@mantine/core';
import { getInspectionById, getImageUrl } from '../api/client';

interface InspectionDetailProps { id: number | null; opened: boolean; onClose: () => void; }
interface InspectionData { id: number; part_id: string; result: string; defect_class: string | null; station: string; confidence: number; timestamp: string; error_code: string | null; image_id: number | null; }

export default function InspectionDetail({ id, opened, onClose }: InspectionDetailProps) {
  const [data, setData] = useState<InspectionData | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id || !opened) return;
    setLoading(true);
    getInspectionById(id).then((res) => { setData(res.data); if (res.data.image_id) return getImageUrl(res.data.image_id); return null; })
      .then((imgRes) => { if (imgRes) setImageUrl(imgRes.data.url || imgRes.data); })
      .catch(() => { setData(null); setImageUrl(null); })
      .finally(() => setLoading(false));
  }, [id, opened]);

  return (
    <Modal opened={opened} onClose={onClose} title={<Title order={4}>Inspection Detail</Title>} size="lg">
      {loading ? <Stack><Skeleton h={30} /><Skeleton h={30} /><Skeleton h={200} /></Stack>
      : data ? <Stack>
        <SimpleGrid cols={2}>
          <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Part ID</Text><Text fw={600}>{data.part_id}</Text></Paper>
          <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Result</Text><Badge color={data.result === 'OK' ? 'green' : 'red'} size="lg">{data.result}</Badge></Paper>
          <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Defect Class</Text><Text fw={600}>{data.defect_class || 'N/A'}</Text></Paper>
          <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Station</Text><Text fw={600}>{data.station}</Text></Paper>
          <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Confidence</Text><Text fw={600}>{(data.confidence * 100).toFixed(1)}%</Text></Paper>
          <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Error Code</Text><Text fw={600}>{data.error_code || 'None'}</Text></Paper>
        </SimpleGrid>
        <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed">Timestamp</Text><Text fw={600}>{new Date(data.timestamp).toLocaleString()}</Text></Paper>
        {imageUrl && <Paper withBorder p="sm" radius="md"><Text size="xs" c="dimmed" mb="xs">Defect Image</Text><Image src={imageUrl} alt="Defect" radius="md" fit="contain" height={250} /></Paper>}
      </Stack>
      : <Text c="dimmed">Failed to load inspection details</Text>}
    </Modal>
  );
}
