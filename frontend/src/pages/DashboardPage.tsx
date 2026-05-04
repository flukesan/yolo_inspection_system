import { Title, SimpleGrid } from '@mantine/core';
import StatsPanel from '../components/StatsPanel';
import LiveCamera from '../components/LiveCamera';
import TrendChart from '../components/TrendChart';
import DefectBreakdown from '../components/DefectBreakdown';
import AlertPanel from '../components/AlertPanel';
import PLCStatus from '../components/PLCStatus';
import SystemHealth from '../components/SystemHealth';

export default function DashboardPage() {
  return <>
    <Title order={3} mb="md">Dashboard</Title>
    <AlertPanel />
    <StatsPanel />
    <SimpleGrid cols={{ base: 1, lg: 3 }} mt="md" spacing="md"><LiveCamera /><TrendChart /><DefectBreakdown /></SimpleGrid>
    <SimpleGrid cols={{ base: 1, sm: 2 }} mt="md" spacing="md"><PLCStatus /><SystemHealth /></SimpleGrid>
  </>;
}
