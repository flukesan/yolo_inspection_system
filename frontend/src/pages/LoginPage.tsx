import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TextInput, PasswordInput, Button, Paper, Title, Text, Container, Alert, Stack } from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { login, setAuth } from '../api/client';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await login(username, password);
      setAuth(res.data.access_token, res.data.refresh_token, res.data.user);
      navigate('/dashboard');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Login failed. Check credentials.';
      setError(msg);
    } finally { setLoading(false); }
  };

  return (
    <Container size={420} mt="15vh">
      <Title ta="center" c="orange.5" fw={900}>YOLO Inspection</Title>
      <Text c="dimmed" size="sm" ta="center" mt={5}>Industrial Quality Control System v2.0</Text>
      <Paper withBorder shadow="md" p={30} mt={30} radius="md">
        <form onSubmit={handleSubmit}>
          <Stack>
            {error && <Alert icon={<IconAlertCircle size={16} />} color="red" variant="filled">{error}</Alert>}
            <TextInput label="Username" placeholder="operator or engineer" value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
            <PasswordInput label="Password" placeholder="Your password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            <Button type="submit" fullWidth mt="md" loading={loading} color="orange">Sign in</Button>
          </Stack>
        </form>
      </Paper>
      <Text c="dimmed" size="xs" ta="center" mt="xl">Default accounts: operator / operator123 :: engineer / engineer123</Text>
    </Container>
  );
}
