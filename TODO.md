# YOLO Inspection System v2.0 — Implementation TODO

> 5 Phases | 6 Weeks | Progress: **73%** (4 of 5 phases done)

---

## 📊 Progress Overview

| Phase | Priority | Status |
|-------|----------|--------|
| Phase 1: Foundation | 🔴 Critical | ✅ DONE — 15 files, Docker + Config + DB |
| Phase 2: PLC Agent | 🔴 Critical | ✅ DONE — 6 files, S7Comm + Simulator + Tests |
| Phase 3: Web Backend | 🟡 High | ✅ DONE — 11 files, FastAPI + Auth + REST + WS |
| Phase 4: Frontend | 🟡 High | ✅ DONE — 19 files, Mantine Dashboard + Auth + Charts |
| Phase 5: Integration | 🔴 Critical | ⬜ Pending — 0/26 |

---

## Phase 3: Web Backend ✅ DONE

> Commit: `7de6661` — 11 files, +1267/-12

### Files Created
| File | Description |
|------|-------------|
| `server/config.py` | YAML + env loader (pydantic-settings) |
| `server/database.py` | asyncpg pool with graceful fallback |
| `server/redis_client.py` | Streams + Pub/Sub with fallback |
| `server/auth.py` | JWT + OAuth2 + RBAC (operator/engineer) |
| `server/minio_client.py` | Image upload/presigned URL |
| `server/routes/auth.py` | POST /login, /refresh, GET /me |
| `server/routes/inspection.py` | POST /inspection, GET /inspections, /stats, /trend, /plc/status |
| `server/routes/images.py` | POST /upload, GET /{name}, /{name}/url |
| `server/routes/websocket.py` | WS /ws/live, /ws/camera |
| `server/main.py` | FastAPI lifespan, health check, route wiring |
| `tests/unit/test_backend.py` | 15 tests (auth + API) |

### API Endpoints
```
POST /api/auth/login          ✅ JWT token
POST /api/auth/refresh        ✅ Refresh token
GET  /api/auth/me             ✅ Current user
POST /api/inspection          ✅ Record result
GET  /api/inspections          ✅ List + filters + pagination
GET  /api/inspection/{id}     ✅ Single record
GET  /api/stats               ✅ Real-time OK/NG stats
GET  /api/stats/trend         ✅ Hourly/daily trend
GET  /api/plc/status          ✅ PLC heartbeat status
POST /api/images/upload       ✅ Defect image upload
GET  /api/images/{name}       ✅ Proxied from MinIO
GET  /api/images/{name}/url   ✅ Presigned URL
WS   /ws/live                 ✅ Real-time inspection feed
WS   /ws/camera               ✅ Frame streaming
GET  /api/health              ✅ Docker HEALTHCHECK
```

---

---

## Phase 4: React Frontend ✅ DONE

> 3 MCP commits — 19 source files, production build: 216KB CSS + 948KB JS

### Files Created
| File | Description |
|------|-------------|
| `frontend/src/theme.ts` | Mantine dark theme — industrial palette |
| `frontend/src/api/client.ts` | Axios + JWT interceptor + auth helpers |
| `frontend/src/App.tsx` | Router: /login, /dashboard, /history, /settings |
| `frontend/src/components/AppShell.tsx` | Sidebar + header + user dropdown + logout |
| `frontend/src/components/AuthGuard.tsx` | Protected route wrapper + auto-refresh |
| `frontend/src/components/LiveCamera.tsx` | WebSocket camera view + connection badge |
| `frontend/src/components/StatsPanel.tsx` | RingProgress gauge + OK/NG counters |
| `frontend/src/components/TrendChart.tsx` | Recharts 24h line chart + mock fallback |
| `frontend/src/components/DefectBreakdown.tsx` | Recharts donut pie chart |
| `frontend/src/components/AlertPanel.tsx` | WebSocket NG popup notifications |
| `frontend/src/components/PLCStatus.tsx` | Heartbeat LED + uptime |
| `frontend/src/components/SystemHealth.tsx` | DB/Redis/MinIO status cards |
| `frontend/src/components/InspectionDetail.tsx` | Modal with full detail + defect image |
| `frontend/src/pages/LoginPage.tsx` | Username/password form + JWT storage |
| `frontend/src/pages/DashboardPage.tsx` | Layout: Camera + Stats + Charts + Status |
| `frontend/src/pages/HistoryPage.tsx` | Table + filter bar + pagination + CSV export |
| `frontend/src/pages/SettingsPage.tsx` | Camera/YOLO/PLC tabs, engineer-only |
| `frontend/vite.config.ts` | Dev proxy → backend :8000 |
| `frontend/index.html` | Dark HTML shell |

### Component Architecture
```
App
└── MantineProvider (dark theme)
    └── BrowserRouter
        ├── /login → LoginPage
        └── AuthGuard
            └── AppShell (sidebar + header)
                ├── /dashboard → DashboardPage
                │   ├── AlertPanel (WebSocket NG)
                │   ├── StatsPanel (RingProgress + stat cards)
                │   ├── LiveCamera (WebSocket status)
                │   ├── TrendChart (Recharts 24h line)
                │   ├── DefectBreakdown (Recharts pie)
                │   ├── PLCStatus (heartbeat LED)
                │   └── SystemHealth (DB/Redis/MinIO)
                ├── /history → HistoryPage
                │   └── InspectionDetail (modal)
                └── /settings → SettingsPage (engineer-only)
```

### Tech Stack
- React 19 + TypeScript + Vite 8
- Mantine v7 (AppShell, Notifications, RingProgress, Table)
- Recharts (LineChart, PieChart)
- React Router v7 (BrowserRouter)
- Axios (JWT interceptor + auto-refresh)
- @tabler/icons-react (icons)

## 📈 Overall Progress: 73%

```
Phase 1 ████████████ ✅ Docker, Config, DB
Phase 2 ████████████ ✅ PLC Agent, Simulator
Phase 3 ████████████ ✅ Backend API, Auth
Phase 4 ████████████ ✅ React Dashboard, 17 components
Phase 5 ░░░░░░░░░░░░ ⬜ Integration, Prod
```
