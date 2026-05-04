# YOLO Inspection System v2.0 — Implementation TODO

> 🏗️ Migration: PyQt6 Desktop → Industrial Web Platform  
> 📋 5 Phases | 6 Weeks | 55 Tasks  
> 🔗 Reference: [GRAPH_REPORT.md](GRAPH_REPORT.md)

---

## 📊 Progress Overview

| Phase | Tasks | Priority | Timeline | Status |
|-------|-------|----------|----------|--------|
| Phase 1: Foundation | 22 | 🔴 Critical | Week 1-2 | ✅ DONE (2026-05-04) |
| Phase 2: PLC Agent | 17 | 🔴 Critical | Week 2-3 | ⬜ Pending |
| Phase 3: Web Backend | 31 | 🟡 High | Week 3-4 | ⬜ Pending |
| Phase 4: Frontend | 24 | 🟡 High | Week 4-5 | ⬜ Pending |
| Phase 5: Integration & Hardening | 26 | 🔴 Critical | Week 5-6 | ⬜ Pending |

---

## Phase 1: Foundation (Week 1-2) ✅ COMPLETED 2026-05-04

### 1.1 Project Structure
- [x] **P1.1.1** ~~สร้าง branch `feature/v2-foundation`~~ → working on `claude/quality-inspection-system-...`
- [x] **P1.1.2** สร้างโครงสร้างโฟลเดอร์ v2 — `edge/`, `server/`, `frontend/`, `tests/`, `docker/`, `docs/`
- [ ] **P1.1.3** ย้าย v1 code เข้า `docs/legacy/` (เก็บไว้ reference) → **defer to Phase 5**

### 1.2 Docker Infrastructure
- [x] **P1.2.1** `docker-compose.yml` — 6 services (inference-engine, api-server, dashboard, postgres, redis, minio)
- [x] **P1.2.2** `docker/Dockerfile.edge` — Python 3.11 + ONNX Runtime + snap7 + GStreamer
- [x] **P1.2.3** `docker/Dockerfile.api` — Python 3.11 + FastAPI + asyncpg + redis-py
- [x] **P1.2.4** `docker/Dockerfile.frontend` — Node 22 + React + Vite + Nginx (multi-stage)

### 1.3 Config Migration
- [x] **P1.3.1** `config/app_config.yaml` — migrated from JSON
- [x] **P1.3.2** Config sections: `camera`, `yolo`, `inspection`, `plc`, `mqtt`, `redis`, `postgres`, `minio`, `auth`, `logging`
- [x] **P1.3.3** `.env.template` — PLC_HOST, DB_PASSWORD, SECRET_KEY, MINIO_ACCESS_KEY

### 1.4 Model Conversion
- [ ] **P1.4.1** Convert YOLOv8 `.pt` → ONNX → **deferred (pending: model file)**
- [ ] **P1.4.2** Quantize ONNX → INT8 → **deferred (pending: P1.4.1)**
- [ ] **P1.4.3** Benchmark accuracy vs speed → **deferred**
- [ ] **P1.4.4** Test ONNX on RPi 5 → **deferred**

### 1.5 Database Schema
- [x] **P1.5.1** PostgreSQL schema — `users`, `inspections`, `defect_events`, `plc_events`, `health_log`
- [x] **P1.5.2** Migration script — `server/migrations/001_init.sql` (schema + indexes + seed data)
- [x] **P1.5.3** SQLite edge buffer — `server/migrations/002_edge_buffer.sql` (WAL mode, auto-vacuum)

### 1.6 Scaffold Code
- [x] **P1.6.1** `edge/main.py` — async entry point with signal handling
- [x] **P1.6.2** `server/main.py` — FastAPI app with `/api/health`, `/api/info`
- [x] **P1.6.3** `requirements.edge.txt` — ONNX Runtime + snap7 + Redis + GStreamer deps
- [x] **P1.6.4** `requirements.api.txt` — FastAPI + asyncpg + JWT + MinIO deps

---

## Phase 2: PLC Agent (Week 2-3) 🔴 MOST CRITICAL

### 2.1 S7Comm Communication
- [ ] **P2.1.1** Implement `edge/plc_agent.py::S7PLCAgent` — connection management (connect/disconnect/reconnect)
- [ ] **P2.1.2** Implement trigger monitoring — poll DB1.DBX0.0 ทุก 10ms, rising edge detection
- [ ] **P2.1.3** Implement result write — OK/NG bits to DB2, error code to DBW2
- [ ] **P2.1.4** Implement heartbeat — DB3 bidirectional ping/pong, 3s timeout
- [ ] **P2.1.5** Implement auto-reconnect with exponential backoff (1s → 2s → 4s → ... max 60s)

### 2.2 PLC Data Block Design
- [ ] **P2.2.1** ออกแบบ DB1 (Trigger): DBX0.0=Trigger, DBW2=TriggerSeqNum, DBW4=StationID
- [ ] **P2.2.2** ออกแบบ DB2 (Result): DBX0.0=OK, DBX0.1=NG, DBW2=ErrorCode, DBW4=DefectClass
- [ ] **P2.2.3** ออกแบบ DB3 (Heartbeat): DBX0.0=EdgePing, DBX1.0=PLCPong, DBW2=PLCTimestamp
- [ ] **P2.2.4** เขียน specification สำหรับ TIA Portal programmer
- [ ] **P2.2.5** สร้าง `edge/plc_enums.py` — InspectionResult(OK/NG/TIMEOUT/ERROR), ErrorCode enum

### 2.3 PLC Simulator
- [ ] **P2.3.1** สร้าง `tests/simulators/plc_simulator.py` — จำลอง S7-300 behavior
- [ ] **P2.3.2** Implement DB read/write simulation
- [ ] **P2.3.3** Implement trigger pattern (rising edge → wait → read result)
- [ ] **P2.3.4** Implement heartbeat response (toggle pong bit)

### 2.4 PLC Unit Tests
- [ ] **P2.4.1** `test_plc_connect_disconnect` — connect success + failure + reconnect
- [ ] **P2.4.2** `test_trigger_detection` — rising edge, falling edge, noise rejection
- [ ] **P2.4.3** `test_result_write` — OK signal, NG signal, error code accuracy
- [ ] **P2.4.4** `test_heartbeat` — normal, timeout detection, recovery
- [ ] **P2.4.5** `test_auto_reconnect` — disconnect → backoff → reconnect → resume

---

## Phase 3: Web Backend (Week 3-4)

### 3.1 FastAPI Core
- [ ] **P3.1.1** ~~สร้าง `server/main.py`~~ ✅ done (Phase 1)
- [ ] **P3.1.2** สร้าง `server/config.py` — load from `config/app_config.yaml` + `.env`
- [ ] **P3.1.3** สร้าง `server/database.py` — asyncpg connection pool
- [ ] **P3.1.4** สร้าง `server/redis_client.py` — Redis connection + Streams + Pub/Sub

### 3.2 Auth Service
- [ ] **P3.2.1** สร้าง `server/auth.py` — JWT create/verify, OAuth2PasswordBearer
- [ ] **P3.2.2** Implement `/api/auth/login` — username/password → JWT token
- [ ] **P3.2.3** Implement `/api/auth/refresh` — refresh token without re-login
- [ ] **P3.2.4** Implement RBAC — operator (read stats) vs engineer (config + models)
- [ ] **P3.2.5** Add `users` table + seed default accounts (operator/engineer) ✅ done (Phase 1)

### 3.3 REST API Endpoints
- [ ] **P3.3.1** `POST /api/inspection` — record inspection result (from edge device)
- [ ] **P3.3.2** `GET /api/inspections` — query history (pagination + filters: date, part_id, result, station)
- [ ] **P3.3.3** `GET /api/inspection/{id}` — single record detail + defect image URL
- [ ] **P3.3.4** `GET /api/stats` — real-time stats (total, OK, NG, rate, period)
- [ ] **P3.3.5** `GET /api/stats/trend` — hourly/daily trend data (for charts)
- [ ] **P3.3.6** `GET /api/plc/status` — PLC connection + heartbeat status
- [ ] **P3.3.7** `GET /api/health` — health check ✅ done (Phase 1)

### 3.4 WebSocket
- [ ] **P3.4.1** สร้าง `server/ws_manager.py` — connection pool, broadcast
- [ ] **P3.4.2** `WS /ws/live` — subscribe Redis `inspection:live` → push to clients
- [ ] **P3.4.3** `WS /ws/camera` — real-time camera frame streaming (base64 JPEG)
- [ ] **P3.4.4** Implement reconnection handling (client disconnect → cleanup)

### 3.5 Image Storage
- [ ] **P3.5.1** สร้าง `server/minio_client.py` — MinIO upload/download
- [ ] **P3.5.2** `POST /api/images/upload` — upload defect image → return presigned URL
- [ ] **P3.5.3** `GET /api/images/{id}` — get defect image (proxied from MinIO)
- [ ] **P3.5.4** Image retention policy — auto-delete >30 days (MinIO lifecycle)

### 3.6 Backend Tests
- [ ] **P3.6.1** `test_auth.py` — login success, wrong password, expired token, RBAC
- [ ] **P3.6.2** `test_api_inspection.py` — create, query, filter, pagination
- [ ] **P3.6.3** `test_ws.py` — connect, receive message, disconnect
- [ ] **P3.6.4** `test_health.py` — all services healthy, graceful degradation

---

## Phase 4: Frontend (Week 4-5)

### 4.1 Project Scaffold
- [ ] **P4.1.1** `npm create vite@latest frontend -- --template react-ts`
- [ ] **P4.1.2** ติดตั้ง dependencies: `@mantine/core`, `@mantine/hooks`, `@mantine/charts`, `react-router-dom`, `recharts`
- [ ] **P4.1.3** ตั้งค่า Mantine theme — dark mode, industrial color palette (#0D1117, #E67E22, #27AE60)
- [ ] **P4.1.4** ตั้งค่า React Router — `/dashboard`, `/history`, `/settings`, `/login`
- [ ] **P4.1.5** สร้าง `frontend/src/api/client.ts` — axios instance + JWT interceptor

### 4.2 Auth Pages
- [ ] **P4.2.1** `LoginPage.tsx` — username/password form, JWT store in localStorage
- [ ] **P4.2.2** `AuthGuard.tsx` — redirect to /login if no token
- [ ] **P4.2.3** Auto-refresh token before expiry (setInterval check)

### 4.3 Dashboard Components
- [ ] **P4.3.1** `LiveCamera.tsx` — WebSocket JPEG stream, full-screen toggle
- [ ] **P4.3.2** `StatsPanel.tsx` — OK/NG counter + gauge (Mantine RingProgress)
- [ ] **P4.3.3** `TrendChart.tsx` — hourly OK rate line chart (Recharts)
- [ ] **P4.3.4** `DefectBreakdown.tsx` — pie chart: defect class distribution
- [ ] **P4.3.5** `AlertPanel.tsx` — NG flash notification (Mantine Notification)

### 4.4 History Page
- [ ] **P4.4.1** `InspectionLog.tsx` — data table (Mantine Table) + pagination
- [ ] **P4.4.2** Filter bar — date range, part_id, result (OK/NG), station
- [ ] **P4.4.3** `InspectionDetail.tsx` — modal with full details + defect image
- [ ] **P4.4.4** Export to CSV button (client-side, CSV download)

### 4.5 Settings Page (Engineer only)
- [ ] **P4.5.1** `SettingsPage.tsx` — tabs: Camera, YOLO, PLC, MQTT
- [ ] **P4.5.2** Camera settings — resolution, FPS, exposure, trigger mode
- [ ] **P4.5.3** YOLO settings — confidence threshold, IoU threshold, model select
- [ ] **P4.5.4** PLC settings — IP, rack, slot, DB layout, heartbeat interval
- [ ] **P4.5.5** Save settings → `PUT /api/settings` (requires engineer role)

### 4.6 System Status
- [ ] **P4.6.1** `PLCStatus.tsx` — heartbeat LED (green/red), connection uptime
- [ ] **P4.6.2** `SystemHealth.tsx` — DB status, Redis status, MinIO status
- [ ] **P4.6.3** Error log viewer (last 100 lines, auto-scroll)

---

## Phase 5: Integration & Hardening (Week 5-6)

### 5.1 End-to-End Integration
- [ ] **P5.1.1** Integration test: PLC trigger → camera → inference → interlock → dashboard
- [ ] **P5.1.2** Test with PLC simulator (full pipeline)
- [ ] **P5.1.3** Test with physical USB camera (if available)
- [ ] **P5.1.4** Test with sample defect images (pre-recorded)

### 5.2 Performance Testing
- [ ] **P5.2.1** Measure end-to-end latency: trigger → result write (target <100ms)
- [ ] **P5.2.2** Benchmark ONNX INT8 vs FP16 vs FP32 accuracy + speed
- [ ] **P5.2.3** Load test: 1000 inspections/minute sustained
- [ ] **P5.2.4** WebSocket latency: event → dashboard display (target <50ms)
- [ ] **P5.2.5** Database query performance: 1M records + pagination

### 5.3 Failover Testing
- [ ] **P5.3.1** Test: Redis crash — SQLite buffer → auto-recover when Redis returns
- [ ] **P5.3.2** Test: PLC disconnect — heartbeat timeout → alert → auto-reconnect
- [ ] **P5.3.3** Test: Camera timeout — frame not received → error code 0xE001 → PLC
- [ ] **P5.3.4** Test: PostgreSQL crash — API returns 503, dashboard shows "offline"
- [ ] **P5.3.5** Test: Power cycle recovery — Docker auto-restart, state restore

### 5.4 Raspberry Pi 5 Deployment
- [ ] **P5.4.1** Build Docker images for `linux/arm64`
- [ ] **P5.4.2** Deploy to RPi 5 — `docker compose up -d`
- [ ] **P5.4.3** Benchmark inference on ARM64 (INT8 ONNX Runtime with ARM NN)
- [ ] **P5.4.4** Optimize memory: Docker limits, swap disabled, GPU memory split
- [ ] **P5.4.5** Test camera: GStreamer v4l2src pipeline on Raspberry Pi OS

### 5.5 Production Readiness
- [ ] **P5.5.1** TLS/HTTPS — self-signed cert for OT network, Let's Encrypt for IT
- [ ] **P5.5.2** Secrets management — `.env` file, Docker secrets, HashiCorp Vault (optional)
- [ ] **P5.5.3** Log rotation — Docker json-file driver + max-size + max-file
- [ ] **P5.5.4** Monitoring — Prometheus metrics endpoint + Grafana dashboard
- [ ] **P5.5.5** Backup strategy — PostgreSQL pg_dump cron, MinIO mirror
- [ ] **P5.5.6** Health check endpoints for all services (Docker HEALTHCHECK) ✅ done (Phase 1)
- [ ] **P5.5.7** Documentation: `docs/DEPLOYMENT.md`, `docs/OPERATIONS.md`

### 5.6 Archive & Cleanup
- [ ] **P5.6.1** Move v1 code to `docs/legacy/v1/`
- [ ] **P5.6.2** Update `README.md` for v2 installation
- [ ] **P5.6.3** Create `CHANGELOG.md` — v2.0.0 release notes
- [ ] **P5.6.4** Tag release: `git tag v2.0.0-beta`

---

## 📊 Task Summary

| Category | Count | Key Deliverable |
|----------|-------|-----------------|
| 🐳 Docker | 4/4 ✅ | docker-compose.yml + 3 Dockerfiles |
| 🔌 PLC | 0/17 | plc_agent.py + PLC simulator + DB spec |
| 🌐 Backend | 2/31 | FastAPI server + Auth + WebSocket + MinIO |
| ⚛️ Frontend | 0/24 | React dashboard (5 components) |
| 🧪 Tests | 0/13 | Unit + Integration + Performance + Failover |
| 📦 Config/DB | 6/6 ✅ | YAML config + PostgreSQL schema + SQLite buffer |
| 🔒 Production | 1/7 | TLS, secrets, monitoring, backup, docs |

**Phase 1: 15/22 completed (4 deferred for model file)**

---

## 🚦 Critical Path (Dependencies)

```
Phase 1 (Foundation) ✅ DONE
  ├── Phase 2 (PLC Agent) ──────┐
  ├── Phase 3 (Backend) ────────┤── Phase 5 (Integration)
  └── Phase 4 (Frontend) ───────┘
```

- **Phase 2, 3, 4 can run in PARALLEL** after Phase 1 completes
- **Phase 5 requires ALL previous phases** completed

---

## 🔴 Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| snap7 library compatibility with S7-300 firmware version | 🔴 High | Test with PLC simulator first; have OPC UA fallback |
| ONNX INT8 accuracy drop >2% | 🟡 Medium | Fallback to FP16 + TensorRT on x86; accept FP32 on ARM64 |
| Raspberry Pi 5 GStreamer v4l2 driver missing | 🟡 Medium | Test on clean Raspberry Pi OS image early in Phase 1 |
| Docker multi-arch build fails on ARM64 | 🟡 Medium | Build on RPi 5 directly as fallback |
| PLC programmer unavailable for DB layout approval | 🔴 High | Provide detailed spec document (P2.2.4); use simulator as reference |
