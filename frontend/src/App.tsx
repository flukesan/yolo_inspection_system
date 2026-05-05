import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';
import '@mantine/charts/styles.css';
import { theme } from './theme';
import AppShell from './components/AppShell';
import AuthGuard from './components/AuthGuard';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';
import SettingsPage from './pages/SettingsPage';
import PlcMonitorPage from './pages/PlcMonitorPage';

export default function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AuthGuard><AppShell /></AuthGuard>}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/plc-monitor" element={<PlcMonitorPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </MantineProvider>
  );
}
