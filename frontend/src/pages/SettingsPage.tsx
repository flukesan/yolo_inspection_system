import { useState, useEffect } from 'react';
import { Paper, Title, Tabs, TextInput, NumberInput, Button, Select, Stack, Text, Alert, Group, Badge, Image, Grid } from '@mantine/core';
import { IconCheck, IconAlertCircle, IconRefresh, IconCamera } from '@tabler/icons-react';
import { useNavigate } from 'react-router-dom';
import { isEngineer, getUser, getCameraConfig, updateCameraConfig, restartCamera, getCameraSnapshot, testPlcConnection, getPlcStatus, getPlcData } from '../api/client';

const SOURCE_TYPES = [
  { value: 'usb', label: 'USB / Notebook Camera' },
  { value: 'rtsp', label: 'RTSP Stream' },
  { value: 'http', label: 'IP Camera (HTTP)' },
  { value: 'gstreamer', label: 'GigE Vision (GStreamer)' },
];

const RESOLUTIONS = ['640x480', '1280x720', '1920x1080', '2560x1440', '3840x2160'];

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Camera state
  const [camSource, setCamSource] = useState('0');
  const [camType, setCamType] = useState('usb');
  const [camWidth, setCamWidth] = useState(1920);
  const [camHeight, setCamHeight] = useState(1080);
  const [camFps, setCamFps] = useState(30);
  const [camQuality, setCamQuality] = useState(65);
  const [camConnected, setCamConnected] = useState(false);
  const [camActual, setCamActual] = useState('');
  const [snapshot, setSnapshot] = useState<string | null>(null);
  const [error, setError] = useState('');

  // YOLO state
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.5);
  const [iouThreshold, setIouThreshold] = useState(0.45);
  const [modelSelect, setModelSelect] = useState('yolov8n_defect');

  // PLC state
  const [plcIp, setPlcIp] = useState('192.168.1.10');
  const [plcRack, setPlcRack] = useState(0);
  const [plcSlot, setPlcSlot] = useState(2);
  const [heartbeatInterval, setHeartbeatInterval] = useState(3);
  const [plcStatus, setPlcStatus] = useState<{connected:boolean, mock_mode:boolean, host:string} | null>(null);
  const [plcTestResult, setPlcTestResult] = useState('');
  const [plcTesting, setPlcTesting] = useState(false);

  useEffect(() => { if (!isEngineer()) navigate('/dashboard'); }, [navigate]);

  useEffect(() => {
    getCameraConfig().then(res => {
      const c = res.data;
      setCamSource(c.source);
      setCamType(c.source_type);
      setCamWidth(c.width);
      setCamHeight(c.height);
      setCamFps(c.fps);
      setCamQuality(c.jpeg_quality);
      setCamConnected(c.connected);
      setCamActual(c.actual_resolution);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    getPlcStatus().then(res => setPlcStatus(res.data)).catch(() => {});
  }, []);

  const sourceHint = () => {
    switch (camType) {
      case 'usb': return 'Device index (0=built-in, 1=USB, 2=... )';
      case 'rtsp': return 'rtsp://user:pass@192.168.1.100:554/stream';
      case 'http': return 'http://192.168.1.100:8080/video';
      case 'gstreamer': return 'gstreamer:aravissrc camera-name=...';
      default: return '';
    }
  };

  const handleApplyCamera = async () => {
    setLoading(true); setError('');
    try {
      const res = await updateCameraConfig({source:camSource,width:camWidth,height:camHeight,fps:camFps,jpeg_quality:camQuality});
      setCamConnected(res.data.connected);
      if (res.data.info) { setCamActual(res.data.info.actual); setCamType(res.data.info.source_type); }
      setSaved(true); setTimeout(() => setSaved(false), 3000);
    } catch (e: unknown) {
      setError((e as {response?:{data?:{detail?:string}}})?.response?.data?.detail || 'Failed');
    } finally { setLoading(false); }
  };

  const handleRestart = async () => {
    setLoading(true);
    try {
      const res = await restartCamera();
      setCamConnected(res.data.connected);
      if (res.data.info) setCamActual(res.data.info.actual);
    } catch { setError('Restart failed'); }
    finally { setLoading(false); }
  };

  const handleSnapshot = async () => {
    try {
      const res = await getCameraSnapshot();
      setSnapshot(`data:image/jpeg;base64,${res.data.image}`);
    } catch { setError('Snapshot failed'); }
  };

  const handleSave = () => { setSaved(true); setTimeout(() => setSaved(false), 3000); };

  const handleTestPlc = async () => {
    setPlcTesting(true); setPlcTestResult('');
    try {
      const res = await testPlcConnection();
      const r = res.data;
      setPlcTestResult(r.ok ? `✅ Connected to ${r.host} — CPU: ${r.cpu||'unknown'}` : `❌ ${r.message}${r.mock_fallback?' (using mock)':''}`);
    } catch {
      setPlcTestResult('❌ Connection test failed');
    } finally { setPlcTesting(false); }
  };

  return <>
    <Title order={3} mb="md">Settings</Title>
    <Text size="sm" c="dimmed" mb="md">Logged in as: {getUser()?.username} ({getUser()?.role})</Text>
    <Tabs defaultValue="camera">
      <Tabs.List mb="md"><Tabs.Tab value="camera">📷 Camera</Tabs.Tab><Tabs.Tab value="yolo">🧠 YOLO</Tabs.Tab><Tabs.Tab value="plc">🔌 PLC</Tabs.Tab></Tabs.List>
      
      <Tabs.Panel value="camera">
        <Paper withBorder p="lg" radius="md"><Stack>
          <Group><Badge size="lg" color={camConnected?'green':'red'}>{camConnected?'🟢 CONNECTED':'🔴 OFFLINE'}</Badge>{camActual&&<Badge size="lg" color="dark" variant="light">{camActual}</Badge>}</Group>
          {error&&<Alert icon={<IconAlertCircle size={16}/>} color="red" variant="light" onClose={()=>setError('')} withCloseButton>{error}</Alert>}
          <Grid>
            <Grid.Col span={7}><Stack>
              <Select label="Source Type" data={SOURCE_TYPES} value={camType} onChange={(v)=>{if(v){setCamType(v);setCamSource(v==='usb'?'0':'')}}}/>
              <TextInput label="Source" description={sourceHint()} value={camSource} onChange={(e)=>setCamSource(e.currentTarget.value)} placeholder={sourceHint()}/>
              <Select label="Resolution" data={RESOLUTIONS} value={`${camWidth}x${camHeight}`} onChange={(v)=>{if(v){const[w,h]=v.split('x').map(Number);setCamWidth(w);setCamHeight(h)}}}/>
              <NumberInput label="FPS" min={1} max={60} value={camFps} onChange={(v)=>setCamFps(Number(v))}/>
              <NumberInput label="JPEG Quality" min={10} max={100} value={camQuality} onChange={(v)=>setCamQuality(Number(v))}/>
            </Stack></Grid.Col>
            <Grid.Col span={5}>
              <Paper withBorder p="sm" radius="md" h={280} style={{display:'flex',alignItems:'center',justifyContent:'center',background:'#111'}}>
                {snapshot?<Image src={snapshot} alt="Snapshot" fit="contain" h="100%"/>:<Stack align="center" gap="xs"><IconCamera size={48} stroke={1} color="gray"/><Text size="sm" c="dimmed">No preview</Text></Stack>}
              </Paper>
            </Grid.Col>
          </Grid>
          <Group><Button color="orange" onClick={handleApplyCamera} loading={loading}>Apply & Restart</Button><Button variant="light" leftSection={<IconRefresh size={16}/>} onClick={handleRestart}>Reconnect</Button><Button variant="subtle" leftSection={<IconCamera size={16}/>} onClick={handleSnapshot}>Snapshot</Button></Group>
          {saved&&<Alert icon={<IconCheck size={16}/>} color="green" variant="filled">Applied</Alert>}
        </Stack></Paper>
      </Tabs.Panel>

      <Tabs.Panel value="yolo"><Paper withBorder p="lg" radius="md"><Stack>
        <Select label="Model" data={[{value:'yolov8n_defect',label:'YOLOv8 Nano'},{value:'yolov8s_defect',label:'YOLOv8 Small'},{value:'yolov8m_defect',label:'YOLOv8 Medium'}]} value={modelSelect} onChange={(v)=>v&&setModelSelect(v)}/>
        <NumberInput label="Confidence Threshold" min={0.1} max={1.0} step={0.05} decimalScale={2} value={confidenceThreshold} onChange={(v)=>setConfidenceThreshold(Number(v))}/>
        <NumberInput label="IoU Threshold" min={0.1} max={1.0} step={0.05} decimalScale={2} value={iouThreshold} onChange={(v)=>setIouThreshold(Number(v))}/>
      </Stack></Paper></Tabs.Panel>

      <Tabs.Panel value="plc"><Paper withBorder p="lg" radius="md"><Stack>
        {plcStatus&&<Group><Badge size="lg" color={plcStatus.connected?'green':'red'}>{plcStatus.connected?'🟢 CONNECTED':'🔴 OFFLINE'}</Badge>{plcStatus.mock_mode&&<Badge size="lg" color="yellow" variant="light">MOCK MODE</Badge>}<Text size="sm" c="dimmed">Host: {plcStatus.host}</Text></Group>}
        {plcTestResult&&<Alert color={plcTestResult.startsWith('✅')?'green':'red'} variant="light">{plcTestResult}</Alert>}
        <TextInput label="PLC IP Address" value={plcIp} onChange={(e)=>setPlcIp(e.currentTarget.value)}/>
        <NumberInput label="Rack" min={0} max={15} value={plcRack} onChange={(v)=>setPlcRack(Number(v))}/>
        <NumberInput label="Slot" min={0} max={15} value={plcSlot} onChange={(v)=>setPlcSlot(Number(v))}/>
        <NumberInput label="Heartbeat Interval (s)" min={1} max={30} value={heartbeatInterval} onChange={(v)=>setHeartbeatInterval(Number(v))}/>
        <Button color="cyan" onClick={handleTestPlc} loading={plcTesting}>Test Connection</Button>
      </Stack></Paper></Tabs.Panel>
    </Tabs>
    <Group mt="xl"><Button color="orange" onClick={handleSave}>Save All</Button>{saved&&<Alert icon={<IconCheck size={16}/>} color="green" variant="filled">Saved</Alert>}</Group>
  </>;
}
