import { Paper, Title } from '@mantine/core';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const mockData = [
  { name: 'Scratch', value: 45 },
  { name: 'Dent', value: 28 },
  { name: 'Misalign', value: 18 },
  { name: 'Missing', value: 12 },
  { name: 'Color', value: 7 },
  { name: 'Other', value: 5 },
];

const COLORS = ['#E67E22', '#E74C3C', '#F39C12', '#3498DB', '#9B59B6', '#1ABC9C'];

export default function DefectBreakdown() {
  const data = mockData;
  return (
    <Paper withBorder p="md" radius="md">
      <Title order={4} mb="md">Defect Breakdown</Title>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value"
            label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
            {data.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: '#161B22', border: '1px solid #30363D', borderRadius: 8 }} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Paper>
  );
}
