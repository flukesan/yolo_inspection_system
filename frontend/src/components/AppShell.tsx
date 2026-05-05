import { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { AppShell as MantineAppShell, Burger, Group, Title, NavLink, Text, ActionIcon, Menu, Avatar } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconDashboard, IconHistory, IconSettings, IconLogout, IconUser, IconRobot, IconCpu, IconCamera } from '@tabler/icons-react';
import { clearAuth, getUser } from '../api/client';

const navItems = [
  { label: 'Dashboard', icon: IconDashboard, to: '/dashboard' },
  { label: 'Operation', icon: IconCamera, to: '/operation' },
  { label: 'History', icon: IconHistory, to: '/history' },
  { label: 'PLC Monitor', icon: IconCpu, to: '/plc-monitor' },
  { label: 'Settings', icon: IconSettings, to: '/settings', role: 'engineer' },
];

export default function AppShell() {
  const [opened, { toggle, close }] = useDisclosure(false);
  const navigate = useNavigate();
  const location = useLocation();
  const user = getUser();

  useEffect(() => { close(); }, [location.pathname]);

  const handleLogout = () => { clearAuth(); navigate('/login'); };

  return (
    <MantineAppShell header={{ height: 60 }} navbar={{ width: 250, breakpoint: 'sm', collapsed: { mobile: !opened } }} padding="md" bg="#0D1117">
      <MantineAppShell.Header bg="#161B22" style={{ borderBottom: '1px solid #30363D' }}>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
            <IconRobot size={28} color="#E67E22" />
            <Title order={4} c="orange.5">YOLO Inspection v2.0</Title>
          </Group>
          <Menu shadow="md" width={200}>
            <Menu.Target><ActionIcon variant="subtle" size="lg"><Avatar color="orange" radius="xl" size="sm"><IconUser size={18} /></Avatar></ActionIcon></Menu.Target>
            <Menu.Dropdown>
              <Menu.Label><Text size="xs" c="dimmed">{user?.username || 'User'}</Text><Text size="xs" c="dimmed">{user?.role || 'unknown'}</Text></Menu.Label>
              <Menu.Divider />
              <Menu.Item leftSection={<IconLogout size={14} />} color="red" onClick={handleLogout}>Logout</Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Group>
      </MantineAppShell.Header>
      <MantineAppShell.Navbar p="sm" bg="#161B22" style={{ borderRight: '1px solid #30363D' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          if (item.role && user?.role !== item.role) return null;
          return <NavLink key={item.to} label={item.label} leftSection={<Icon size={20} />} active={location.pathname === item.to} onClick={() => { navigate(item.to); close(); }} variant="filled" color="orange" mb={4} />;
        })}
      </MantineAppShell.Navbar>
      <MantineAppShell.Main><Outlet /></MantineAppShell.Main>
    </MantineAppShell>
  );
}
