# YOLO Inspection System v2.0 — Deployment Guide

## Quick Start
```bash
git clone https://github.com/flukesan/yolo_inspection_system.git
cd yolo_inspection_system && cp .env.production .env && nano .env
docker compose up -d
open http://localhost:5173
```
Default: `engineer/engineer123` | `operator/operator123`

## Hardware
| Platform | CPU | RAM | Disk |
|----------|-----|-----|------|
| Industrial PC | 4-8 cores | 8-16 GB | 200 GB SSD |
| Raspberry Pi 5 | ARM A76 | 8 GB | 64 GB NVMe |

## Deploy
```bash
# Standard
docker compose up -d

# Raspberry Pi 5
docker compose -f docker-compose.yml -f docker-compose.rpi5.yml up -d

# Multi-arch build
./docker/build.sh --push --tag v2.0.0-beta
```

## PLC Setup
S7-300 via S7Comm. DB1=Trigger, DB2=Result, DB3=Heartbeat. See docs/PLC_DB_SPEC.md.

## Security
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/server.key -out certs/server.crt
echo "ENABLE_TLS=true" >> .env
```

## Monitoring
```bash
docker compose -f docker-compose.monitoring.yml up -d
# Grafana: http://localhost:3000 (admin/admin)
```

## Backup
```bash
# Add to crontab
0 2 * * * /opt/yolo/scripts/backup.sh --retention 30
# Restore
docker exec -i postgres psql -U yolo yolo_inspection < backup.sql
```
