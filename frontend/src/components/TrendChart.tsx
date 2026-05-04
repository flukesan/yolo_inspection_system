import { useState, useEffect } from 'react';
import { Paper, Title, Skeleton } from '@mantine/core';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getStatsTrend } from '../api/client';

interface TrendPoint { hour: string; total: number; ok: number; ng: number; ok_rate: number; }

const mockTrend: TrendPoint[] = Array.from({ length: 24 }, (_, i) => ({
  hour: `${String(i).padStart(2, '0')}:00`, total: Math.floor(Math.random() * 200) + 50,
  ok: Math.floor(Math.random() * 190) + 45, ng: Math.floor(Math.random() * 15), ok_rate: 85 + Math.random() * 14,
}));

export default function TrendChart() {
  const [data, setData] = useState<TrendPoint[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStatsTrend().then((res) => setData(res.data)).catch(() => setData(mockTrend)).finally(() => setLoading(false));
    const interval = setInterval(() => { getStatsTrend().then((res) => setData(res.data)).catch(() => setData(mockTrend)); }, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <Skeleton h={300} radius="md" />;
  const chartData = data || mockTrend;

  return (
    <Paper withBorder p="md" radius="md">
      <Title order={4} mb="md">Inspection Trend (24h)</Title>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#30363D" />
          <XAxis dataKey="hour" stroke="#8B949E" fontSize={12} />
          <YAxis stroke="#8B949E" fontSize={12} />
          <Tooltip contentStyle={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: 8 }} />
          <Legend />
          <Line type="monotone" dataKey="ok_rate" stroke="#27AE60" strokeWidth={2} dot={false} name="OK Rate %" />
          <Line type="monotone" dataKey="total" stroke="#E67E22" strokeWidth={2} dot={false} name="Total" />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
}
