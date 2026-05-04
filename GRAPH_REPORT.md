# Codebase Knowledge Graph: YOLO Inspection System v2.0
Generated: 2026-05-04 | Language: Python 3.11+ | Framework: FastAPI + React + YOLOv8 + ONNX | Phase: Architecture Redesign

> 🏗️ **v2 Architecture** — Industrial-grade inspection system: Web GUI, S7Comm PLC interlocking, Redis signal queue, PostgreSQL, Docker multi-arch
> 
> Base: `flukesan/yolo_inspection_system` (branch `claude/quality-inspection-system-...`)  
> v1 GRAPH_REPORT preserved at `docs/GRAPH_REPORT_v1.md`

---

## Architecture Overview (v2)

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOLO INSPECTION SYSTEM v2                     │
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Siemens  │◄──►│  Edge    │◄──►│ Backend  │◄──►│ Frontend │  │
│  │ S7-300   │    │ Device   │    │ FastAPI  │    │ React    │  │
│  │ PLC      │    │ (RPi5)   │    │ Server   │    │ Dashboard│  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       ▲               │                │               │        │
│       │ S7Comm        │ Redis          │ PostgreSQL    │        │
│       ▼               ▼                ▼               ▼        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Conveyor │    │ Camera   │    │ MinIO    │    │ DeviceWise│  │
│  │ / Sorter │    │ GigE/USB │    │ Storage  │    │ (MQTT)   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Entry Points (v2)

| File | Trigger | Role |
|------|---------|------|
| `server.py` | `uvicorn server:app` | 🌐 Primary — FastAPI Web Backend (REST + WebSocket + Auth) |
| `plc_agent.py` | `S7PLCAgent.connect()` | 🔌 PLC Communication Agent (S7Comm trigger + heartbeat) |
| `inference_engine.py` | Camera trigger callback | 🔍 YOLO/ONNX inference pipeline |
| `main.py` (v1) | `if __name__ == "__main__"` | 🏚️ Legacy PyQt6 entry (deprecated in v2) |
| `frontend/src/main.tsx` | React 19 + Vite | ⚛️ Web Dashboard entry |

**v2 Primary flow:** `PLC trigger → plc_agent → camera → inference → plc_agent (interlock) → redis → fastapi → websocket → react`

---

## Dependency Hierarchy (v2)

```
Layer 1: External Triggers & Outputs
  ├── Siemens S7-300 PLC (trigger source, interlock target)
  ├── HMI Panel (manual trigger)
  ├── GigE/USB Camera (frame source)
  └── Conveyor/Sorter (interlock output)

Layer 2: Edge Device (Docker Container Group)
  ├── plc_agent.py::S7PLCAgent          🔌 S7Comm + OPC UA
  │   ├── snap7 (native S7Comm)
  │   └── opcua-asyncio (fallback)
  ├── inference_engine.py::ONNXInference 🔍 ONNX Runtime + YOLOv8
  │   ├── onnxruntime (CPU/CUDA/TensorRT)
  │   └── ultralytics (model conversion only)
  ├── camera_gateway.py::CameraGateway  📷 GStreamer + v4l2
  │   └── harvesters (GigE Vision, optional)
  ├── redis_client.py::SignalQueue      ⚡ Redis Streams
  └── edge_logger.py::EdgeLogger        💾 SQLite edge buffer

Layer 3: Application Server (Docker Container Group)
  ├── server.py::FastAPI App            🌐 REST + WebSocket
  │   ├── auth.py::AuthService          JWT + OAuth2 + RBAC
  │   ├── ws_manager.py::WSManager      WebSocket connection pool
  │   └── stats.py::StatsEngine         Real-time aggregation
  ├── postgres (container)              🗄️ Inspection history
  ├── redis (container)                 ⚡ Pub/Sub + Queue
  └── minio (container)                 🗄️ Defect image archive

Layer 4: Frontend (Docker Container)
  └── React 19 + Vite + Mantine UI      ⚛️ Web Dashboard
      ├── LiveCamera.tsx                Real-time camera feed
      ├── StatsPanel.tsx                Real-time OK/NG counters
      ├── InspectionLog.tsx             Historical data table
      ├── AlertPanel.tsx                Defect alerts
      └── PLCStatus.tsx                 Heartbeat monitor
```

---

## Container Architecture

```
┌────────────────── Docker Compose ──────────────────────┐
│                                                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ inference-  │  │  api-server  │  │   dashboard   │  │
│  │ engine      │  │  (FastAPI)   │  │  (React/Nginx)│  │
│  │ (Edge)      │  │  Port:8000   │  │  Port:3000    │  │
│  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
│         │               │                               │
│  ┌──────┴──────┐  ┌─────┴──────┐  ┌───────────────┐   │
│  │   redis     │  │  postgres  │  │    minio      │   │
│  │  (Queue)    │  │  (History) │  │  (Images)     │   │
│  └─────────────┘  └────────────┘  └───────────────┘   │
│                                                        │
│  Supported: linux/amd64, linux/arm64 (Raspberry Pi 5)  │
└────────────────────────────────────────────────────────┘
```

---

## Core Concepts & Where They Live (v2)

### 🆕 New Components (v2 only)

- **PLC Agent**: `plc_agent.py::S7PLCAgent` — S7Comm native communication with S7-300
  - Trigger monitoring (DB1.DBX0.0 rising edge)
  - Interlocking (OK/NG → DB2, error code → DBW2)
  - Heartbeat (DB3 bidirectional ping/pong)
  - Auto-reconnect with exponential backoff
- **Signal Queue**: Redis Streams — decouples inference from backend
  - Queue: `inspection:results` (edge → server)
  - Pub/Sub: `inspection:live` (server → WebSocket → dashboard)
- **WebSocket Manager**: `ws_manager.py` — real-time dashboard updates
- **Auth Service**: `auth.py` — JWT + OAuth2PasswordBearer, RBAC (operator/engineer)
- **ONNX Inference**: `inference_engine.py::ONNXInference` — ONNX Runtime with ARM NN / CUDA / TensorRT
- **Camera Gateway**: `camera_gateway.py` — GStreamer pipeline, v4l2 hardware decode

### ♻️ Evolved from v1

- **Inspection Engine** → split into `plc_agent.py` + `inference_engine.py`
- **MQTT Client** → remains as `mqtt_client.py` for DeviceWise bridge (read-only in v2)
- **Database** → PostgreSQL (server) + SQLite (edge buffer) — dual-write pattern
- **MainWindow (46KB PyQt6)** → React Dashboard (component-based, ~5KB per component)

### 🗑️ Deprecated

- `main.py::AppController` — replaced by Docker Compose orchestration
- `ui/main_window.py` (46KB PyQt6) — replaced by React + FastAPI
- `utils/plc_communication.py` (Modbus) — replaced by `plc_agent.py` (S7Comm)
- `utils/database.py` (SQLite only) — replaced by PostgreSQL + Redis

---

## Data Flow (v2 — Full Inspection Cycle)

```
[1. TRIGGER]
    │  Siemens S7-300 / HMI writes DB1.DBX0.0 = 1
    │  plc_agent polls every 10ms → detects rising edge
    ▼
[2. CAPTURE]
    │  plc_agent.on_trigger() callback fires
    │  camera_gateway captures frame via GStreamer/v4l2
    ▼
[3. INFERENCE]
    │  ONNX Runtime runs YOLOv8 (INT8 quantized on ARM64)
    │  Output: bounding boxes, class, confidence
    ▼
[4. INTERLOCKING]
    │  plc_agent.send_result(OK/NG) → writes DB2
    │  DBX0.0 = OK, DBX0.1 = NG, DBW2 = error code
    │  PLC reads DB2 → activates conveyor diverter / stops line
    ▼
[5. LOGGING]
    │  ┌─ edge_logger → SQLite (local buffer)
    │  ├─ redis XADD "inspection:results" {json}
    │  ├─ mqtt_client.publish → DeviceWise
    │  └─ minio.upload(defect_image) [if NG]
    ▼
[6. DASHBOARD (async, parallel)]
    │  Redis PUBLISH "inspection:live" → WebSocket
    │  React: StatsPanel update, LiveCamera frame, AlertPanel flash
    ▼
[7. HEARTBEAT (continuous)]
    │  plc_agent toggles DB3.DBX0.0 every 1s
    │  PLC toggles DB3.DBX1.0 in response
    │  If PLC stops responding >3s → EMERGENCY alert
```

---

## Interlocking Sequence

```
TIMELINE (typical: < 100ms end-to-end):

t=0ms    PLC sends trigger (DB1.DBX0.0 ↑)
t=1ms    plc_agent detects trigger
t=2ms    Camera capture (GStreamer pipeline)
t=5ms    Frame → ONNX Runtime
t=30ms   YOLOv8 inference complete
t=31ms   Result classification (OK/NG)
t=32ms   plc_agent writes DB2 (OK/NG bit + error code)
t=33ms   PLC reads DB2 → activates sorter
t=35ms   Redis XADD + PUBLISH
t=36ms   WebSocket → React dashboard update

Total: ~36ms logic + camera exposure + inference time
Target: < 100ms for high-speed production lines
```

---

## File Responsibility Map (v2)

| Category | Files | Status |
|----------|-------|--------|
| **PLC Communication** | `plc_agent.py` | 🆕 NEW |
| **Inference Engine** | `inference_engine.py` (ONNX) | ♻️ REWRITE |
| **Camera Gateway** | `camera_gateway.py` | 🆕 NEW |
| **Signal Queue** | `redis_client.py` | 🆕 NEW |
| **Edge Logger** | `edge_logger.py` | 🆕 NEW |
| **MQTT Bridge** | `mqtt_client.py` | ♻️ KEEP (read-only) |
| **Web Backend** | `server.py`, `auth.py`, `ws_manager.py`, `stats.py` | 🆕 NEW |
| **Database** | PostgreSQL + SQLite (dual-write) | 🆕 NEW |
| **Frontend** | `frontend/src/` (React + Mantine) | 🆕 NEW |
| **Docker** | `docker-compose.yml`, `Dockerfile.edge`, `Dockerfile.api` | 🆕 NEW |
| **Config** | `config/settings.py`, `config/app_config.yaml` | ♻️ EXTEND |
| **Model** | `models/yolov8_defect.onnx` (quantized) | ♻️ CONVERT |
| **YOLO Detector** | `core/yolo_detector.py` | 🗑️ DEPRECATED |
| **PyQt6 UI** | `ui/` (all files) | 🗑️ DEPRECATED |
| **PLC (Modbus)** | `utils/plc_communication.py` | 🗑️ DEPRECATED |
| **Data Logger** | `core/data_logger.py` | 🗑️ DEPRECATED |
| **App Controller** | `main.py::AppController` | 🗑️ DEPRECATED |

---

## Critical Paths (High-Risk Change Areas) — v2

1. **`plc_agent.py` ↔ PLC** — Single point of failure for interlocking. MUST have heartbeat + auto-reconnect. If PLC comm fails, production line may not stop on defect detection.
2. **Redis availability** — If Redis goes down, inspection results queue up in SQLite buffer but real-time dashboard goes dark. Redis should have `restart: always` + health check.
3. **Inference latency on Raspberry Pi 5** — INT8 quantization is MANDATORY for <100ms. Without it, inference may take 300-500ms on ARM64.
4. **Docker networking on factory floor** — Static IP allocation for PLC communication. DHCP changes will break `PLC_HOST` env var.
5. **Auth token expiry during shift** — 8-hour shift. Token expires → operator locked out mid-shift. Implement refresh token or extend to 12h.

---

## Verified ✅ vs Inferred ⚠️ (v2 Reference Architecture)

### Verified ✅ (from v1 source analysis):
- Current codebase structure (47 files, PyQt6 + YOLOv8)
- `InspectionEngine.__init__(camera_manager, yolo_detector, data_logger)` — dependency injection pattern
- `MQTTClient.publish_inspection_result()` — DeviceWise bridge exists
- `PLCCommunication` has Modbus TCP methods — to be replaced by S7Comm
- 50+ PyQt6 signal/slot connections in main_window.py

### ⚠️ Architecture Decisions (awaiting implementation):
- `plc_agent.py` design is based on snap7 S7Comm protocol spec — NOT yet verified against actual S7-300
- ONNX INT8 quantization trade-off: accuracy drop vs speed gain — needs benchmark
- Raspberry Pi 5 GStreamer v4l2 hardware acceleration — depends on kernel/driver version
- Redis Streams maxlen — needs sizing based on production throughput
- JWT refresh token strategy — TO BE DECIDED

---

## Integration Points (v2)

| System | Protocol | Library | Config | Auth |
|--------|----------|---------|--------|------|
| **S7-300 PLC** | S7Comm / OPC UA | `python-snap7` / `opcua-asyncio` | `PLC_HOST`, `PLC_RACK`, `PLC_SLOT` | None (OT network) |
| **DeviceWise IoT** | MQTT | `paho-mqtt` | `MQTT_BROKER`, `MQTT_TOPIC` | TLS cert |
| **GigE Camera** | GenICam | `harvesters` + GStreamer | `CAMERA_DEVICE` | None |
| **Redis** | TCP | `redis-py[asyncio]` | `REDIS_URL` | Password |
| **PostgreSQL** | TCP | `asyncpg` | `DATABASE_URL` | User/Pass |
| **MinIO** | S3 API | `minio-py` | `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY` | Access/Secret key |
| **Frontend → Backend** | HTTPS + WSS | JWT Bearer | `API_BASE_URL` | JWT + OAuth2 |

---

## Migration Path: v1 → v2

### Phase 1: Foundation (Week 1-2)
```
□ Clone v1 as baseline (branch: feature/v2-foundation)
□ Create docker-compose.yml with postgres + redis + minio
□ Create Dockerfile.edge (ONNX Runtime + snap7)
□ Create Dockerfile.api (FastAPI + asyncpg)
□ Set up config/app_config.yaml (migrate from JSON → YAML)
□ Convert YOLOv8 .pt → ONNX → benchmark INT8 accuracy
```

### Phase 2: PLC Agent (Week 2-3)
```
□ Implement plc_agent.py (S7Comm trigger + interlocking + heartbeat)
□ Design PLC DB layout (DB1=trigger, DB2=result, DB3=heartbeat)
□ Create simulator for testing without physical PLC
□ Unit tests: trigger detection, result write, heartbeat timeout
□ Integration test: plc_agent → camera trigger → inference → interlock
```

### Phase 3: Web Backend (Week 3-4)
```
□ Implement server.py (FastAPI + JWT auth)
□ Implement ws_manager.py (WebSocket broadcasting)
□ Implement stats.py (real-time aggregation queries)
□ Implement redis_client.py (XADD + PUBLISH)
□ API tests with pytest + httpx
```

### Phase 4: Frontend (Week 4-5)
```
□ Scaffold React 19 + Vite + Mantine UI
□ LiveCamera.tsx (WebSocket image stream)
□ StatsPanel.tsx (real-time OK/NG counters)
□ InspectionLog.tsx (historical query)
□ AlertPanel.tsx (defect notifications)
□ PLCStatus.tsx (heartbeat monitor)
```

### Phase 5: Integration & Hardening (Week 5-6)
```
□ End-to-end test: PLC trigger → inference → interlock → dashboard
□ Performance test: <100ms latency target
□ Failover test: Redis crash, PLC disconnect, camera timeout
□ Raspberry Pi 5 deployment test
□ Production config: TLS, secrets management, log rotation
□ Archive v1 code to docs/legacy/
```

---

## Notes for AI Coding Agents (v2)

### 🔴 CRITICAL — Before Writing Any Code:
- **The PLC is the system of record for safety** — interlocking logic MUST be correct. A wrong signal can cause physical damage.
- **plc_agent.py** is the most safety-critical file. Use TDD with simulator before touching real PLC.
- **Docker networking MUST use static IP for PLC** — never DHCP on factory OT network.
- **INT8 quantization benchmark FIRST** — if accuracy drops >2%, fallback to FP16 with TensorRT.

### 🟡 When Modifying:
- **Redis Stream naming** (`inspection:results`, `inspection:live`) is a contract — change in one place breaks pub/sub.
- **JWT token claims** must stay minimal (sub, role, exp). Adding claims = re-issue all tokens.
- **PLC DB layout** (DB1/2/3 offsets) is shared between plc_agent.py AND the PLC program (TIA Portal). Change in sync.

### 🟢 Safe-to-Change:
- React component styling (Mantine theme tokens)
- FastAPI endpoint paths (additive only — don't rename existing)
- Docker image tags
- Logging verbosity levels

### ⚠️ Platform-Specific Pitfalls:
```
Raspberry Pi 5:
  - No CUDA. ONNX Runtime with ARM NN or CPU EP only.
  - GStreamer v4l2src works; v4l2h264enc may need firmware update.
  - SD card wear: Mount /var/lib/postgresql to NVMe SSD.
  - GPIO for camera trigger (optional): use RPi.GPIO, pin 7/11.

Windows IPC:
  - snap7 needs 32-bit DLL. Use WSL2 or Docker Linux container.
  - GStreamer on Windows: use ksvideosrc instead of v4l2src.

Linux IPC (x86):
  - Full CUDA support via nvidia-container-toolkit.
  - GigE Vision: ptp4l for PTP clock sync with camera.
```