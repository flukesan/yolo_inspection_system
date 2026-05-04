# YOLO Inspection System v2.0

**Industrial Quality Inspection Platform** — Real-time defect detection with PLC interlocking, Web dashboard, and edge deployment.

> 4-Tier Architecture: PLC ↔ Edge ↔ Backend ↔ Dashboard
> Docker Multi-Arch: AMD64 + ARM64 (Raspberry Pi 5)
> YOLOv8 ONNX Inference with INT8 quantization

## Quick Start
```bash
git clone https://github.com/flukesan/yolo_inspection_system.git
cd yolo_inspection_system && cp .env.production .env
docker compose up -d && open http://localhost:5173
```
Default: `engineer/engineer123` | `operator/operator123`

## Architecture
```
PLC (S7-300) ↔ Edge (Docker) ↔ FastAPI ↔ React Dashboard
              ↕ PostgreSQL + Redis + MinIO
```

## Features
- S7Comm PLC Agent + Simulator + Interlocking
- REST API (15 endpoints) + WebSocket (live + camera)
- React Dashboard (Mantine v7 dark theme, Recharts)
- JWT Auth + RBAC (operator/engineer)
- Docker Multi-Arch (AMD64 + ARM64)
- Prometheus + Grafana monitoring
- Backup script + Deployment docs

## Docs
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Operations Guide](docs/OPERATIONS.md)
- [PLC DB Spec](docs/PLC_DB_SPEC.md)
- [Architecture](GRAPH_REPORT.md)
- [Changelog](CHANGELOG.md)
