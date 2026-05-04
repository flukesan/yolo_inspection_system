import { useState, useEffect } from 'react';
import { Paper, Title, Tabs, TextInput, NumberInput, Button, Select, Stack, Text, Alert, Group } from '@mantine/core';
import { IconCheck } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { isEngineer, getUser } from '../api/client';

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const navigate = useNavigate();

  const [resolution, setResolution] = useState('1920x1080');
  const [fps, setFps] = useState(30);
  const [exposure, setExposure] = useState(0);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [iouThreshold, setIouThreshold] = useState(0.45);
  const [modelSelect, setModelSelect] = useState('yolov8n_defect');
  const [plcIp, setPlcIp] = useState('192.168.1.10');
  const [plcRack, setPlcRack] = useState(0);
  const [plcSlot, setPlcSlot] = useState(2);
  const [heartbeatInterval, setHeartbeatInterval] = useState(3);

  useEffect(() => { if (!isEngineer()) navigate('/dashboard'); }, [navigate]);

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 3000); };

  return <>
    <Title order={3} mb="md">Settings</Title>
    <Text size="sm" c="dimmed" mb="md">Logged in as: {getUser()?.username} ({getUser()?.role})</Text>
    <Tabs defaultValue="camera">
      <Tabs.List mb="md"><Tabs.Tab value="camera">Camera</Tabs.Tab><Tabs.Tab value="yolo">YOLO Model</Tabs.Tab><Tabs.Tab value="plc">PLC</Tabs.Tab></Tabs.List>
      <Tabs.Panel value="camera"><Paper withBorder p="lg" radius="md"><Stack>
        <Select label="Resolution" data={['640x480', '1280x720', '1920x1080', '3840x2160']} value={resolution} onChange={(v) => v && setResolution(v)} />
        <NumberInput label="FPS" min={1} max={120} value={fps} onChange={(v) => setFps(Number(v))} />
        <NumberInput label="Exposure (0 = auto)" min={-10} max={10} value={exposure} onChange={(v) => setExposure(Number(v))} />
      </Stack></Paper></Tabs.Panel>
      <Tabs.Panel value="yolo"><Paper withBorder p="lg" radius="md"><Stack>
        <Select label="Model" data={[{ value: 'yolov8n_defect', label: 'YOLOv8 Nano' }, { value: 'yolov8s_defect', label: 'YOLOv8 Small' }, { value: 'yolov8m_defect', label: 'YOLOv8 Medium' }]} value={modelSelect} onChange={(v) => v && setModelSelect(v)} />
        <NumberInput label="Confidence Threshold" min={0.1} max={1.0} step={0.05} decimalScale={2} value={confidenceThreshold} onChange={(v) => setConfidenceThreshold(Number(v))} />
        <NumberInput label="IoU Threshold" min={0.1} max={1.0} step={0.05} decimalScale={2} value={iouThreshold} onChange={(v) => setIouThreshold(Number(v))} />
      </Stack></Paper></Tabs.Panel>
      <Tabs.Panel value="plc"><Paper withBorder p="lg" radius="md"><Stack>
        <TextInput label="PLC IP Address" value={plcIp} onChange={(e) => setPlcIp(e.currentTarget.value)} />
        <NumberInput label="Rack" min={0} max={15} value={plcRack} onChange={(v) => setPlcRack(Number(v))} />
        <NumberInput label="Slot" min={0} max={15} value={plcSlot} onChange={(v) => setPlcSlot(Number(v))} />
        <NumberInput label="Heartbeat Interval (seconds)" min={1} max={30} value={heartbeatInterval} onChange={(v) => setHeartbeatInterval(Number(v))} />
      </Stack></Paper></Tabs.Panel>
    </Tabs>
    <Group mt="xl"><Button color="orange" onClick={handleSave}>Save Settings</Button>
      {saved && <Alert icon={<IconCheck size={16} />} color="green" variant="filled" style={{ display: 'inline-flex' }}>Settings saved successfully</Alert>}
    </Group>
  </>;
}
