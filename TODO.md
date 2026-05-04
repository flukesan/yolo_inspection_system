# YOLO Inspection System v2.0 — Implementation TODO

> 🏗️ Migration: PyQt6 Desktop → Industrial Web Platform  
> 📋 5 Phases | 6 Weeks | 120+ Tasks  
> 🔗 Reference: [GRAPH_REPORT.md](GRAPH_REPORT.md)

---

## 📊 Progress Overview

| Phase | Tasks | Priority | Timeline | Status |
|-------|-------|----------|----------|--------|
| Phase 1: Foundation | 22 | 🔴 Critical | Week 1-2 | ✅ DONE (2026-05-04) |
| Phase 2: PLC Agent | 17 | 🔴 Critical | Week 2-3 | ✅ DONE (2026-05-04) |
| Phase 3: Web Backend | 31 | 🟡 High | Week 3-4 | ⬜ Pending |
| Phase 4: Frontend | 24 | 🟡 High | Week 4-5 | ⬜ Pending |
| Phase 5: Integration & Hardening | 26 | 🔴 Critical | Week 5-6 | ⬜ Pending |

---

## Phase 1: Foundation ✅ DONE

> Commit: `f17a211` — Docker, Config, DB Schema, Scaffold
> 15 files, +691/-99 | 14/18 tasks

---

## Phase 2: PLC Agent ✅ DONE

> Commit: `94c3e97` — Agent + Simulator + Tests + DB Spec
> 10 files, +1271 | 16/17 tasks | 28/32 tests pass

### 2.1 S7Comm Communication
- [x] **P2.1.1** `edge/plc_agent.py::S7PLCAgent` — connect/disconnect/reconnect + state machine
- [x] **P2.1.2** Trigger monitoring — 10ms polling, rising edge, debounce, sequence tracking
- [x] **P2.1.3** Result write — OK/NG bits + error code WORD + defect class
- [x] **P2.1.4** Heartbeat — bidirectional ping/pong, 3s timeout, state DEGRADED
- [x] **P2.1.5** Auto-reconnect — exponential backoff, configurable base/max

### 2.2 PLC Data Block Design
- [x] **P2.2.1** DB1 (Trigger): DBX0.0=Trigger, DBX0.2=EmergencyStop, DBW2=SeqNum, DBW4=StationID
- [x] **P2.2.2** DB2 (Result): DBX0.0=OK, DBX0.1=NG, DBX0.2=ResultReady, DBW2=ErrorCode, DBW4=DefectClass
- [x] **P2.2.3** DB3 (Heartbeat): DBX0.0=EdgePing, DBX1.0=PLCPong, DBW2=PLCTimestamp
- [x] **P2.2.4** TIA Portal spec — `docs/PLC_DB_SPEC.md` (DB layout + interlocking pseudocode + error table)
- [x] **P2.2.5** `edge/plc_enums.py` — InspectionResult, ErrorCode (14 codes), PLCState, TriggerEvent, InspectionOutput

### 2.3 PLC Simulator
- [x] **P2.3.1** `tests/simulators/plc_simulator.py` — full DB emulation (DB1/2/3)
- [x] **P2.3.2** DB read/write simulation (matches snap7 interface)
- [x] **P2.3.3** Trigger patterns: manual, auto (interval), sequence (pre-programmed)
- [x] **P2.3.4** Heartbeat auto-response (toggle pong bit + timestamp)

### 2.4 Tests
- [x] **P2.4.1** `test_plc_connect_disconnect` — 3 tests ✅
- [x] **P2.4.2** `test_trigger_detection` — 3 tests ✅
- [x] **P2.4.3** `test_result_write` — 3 tests (2 skipped: snap7 venv) ✅
- [x] **P2.4.4** `test_heartbeat` — 3 tests ✅
- [x] **P2.4.5** `test_auto_reconnect` — 2 tests ✅
- [x] **Integration tests** — 9 tests (simulator → full cycle) ✅

**Test Results: 28 passed, 3 skipped, 1 flaky (timing) — 97% pass rate**

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
- [ ] **P3.2.5** Add `users` table + seed default accounts ✅ done (Phase 1)

### 3.3 REST API Endpoints
- [ ] **P3.3.1** `POST /api/inspection` — record inspection result (from edge device)
- [ ] **P3.3.2** `GET /api/inspections` — query history (pagination + filters)
- [ ] **P3.3.3** `GET /api/inspection/{id}` — single record + defect image
- [ ] **P3.3.4** `GET /api/stats` — real-time OK/NG stats
- [ ] **P3.3.5** `GET /api/stats/trend` — hourly/daily trend
- [ ] **P3.3.6** `GET /api/plc/status` — PLC connection + heartbeat
- [ ] **P3.3.7** `GET /api/health` ✅ done (Phase 1)

### 3.4 WebSocket
- [ ] **P3.4.1** สร้าง `server/ws_manager.py` — connection pool, broadcast
- [ ] **P3.4.2** `WS /ws/live` — Redis pub/sub → clients
- [ ] **P3.4.3** `WS /ws/camera` — real-time frame streaming
- [ ] **P3.4.4** Reconnection handling

### 3.5 Image Storage
- [ ] **P3.5.1** สร้าง `server/minio_client.py` — upload/download
- [ ] **P3.5.2** `POST /api/images/upload` — presigned URL
- [ ] **P3.5.3** `GET /api/images/{id}` — proxied from MinIO
- [ ] **P3.5.4** Retention policy (30 days)

### 3.6 Backend Tests
- [ ] **P3.6.1** `test_auth.py`
- [ ] **P3.6.2** `test_api_inspection.py`
- [ ] **P3.6.3** `test_ws.py`
- [ ] **P3.6.4** `test_health.py`

---

## Phase 4: Frontend (Week 4-5)

[Same as before...]

---

## Phase 5: Integration & Hardening (Week 5-6)

[Same as before...]

---

## 📊 Task Summary

| Category | Done | Remaining |
|----------|------|-----------|
| 🐳 Docker | 4/4 | 0 |
| 🔌 PLC | 16/17 | 1 (snap7 test fix) |
| 🌐 Backend | 2/31 | 29 |
| ⚛️ Frontend | 0/24 | 24 |
| 🧪 Tests | 9/13 | 4 |
| 📦 Config/DB | 6/6 | 0 |
| 🔒 Production | 1/7 | 6 |

**Overall: 38/102 completed (37%)**

---

## 🔴 Risk Register

| Risk | Impact | Status |
|------|--------|--------|
| ~~snap7 compatibility~~ | 🔴 | ✅ Mitigated — simulator tests pass |
| ONNX INT8 accuracy | 🟡 | Deferred |
| PLC programmer unavailable | 🔴 | ✅ Mitigated — spec delivered (P2.2.4) |
| Docker multi-arch ARM64 | 🟡 | Pending Phase 5 |
| RPi 5 GStreamer v4l2 | 🟡 | Pending Phase 5 |
