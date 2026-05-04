# YOLO Inspection System v2.0 — Operations Guide

## Dashboard
- **Dashboard** — Live stats, camera, trends, PLC/health status
- **History** — Searchable log + CSV export
- **Settings** — Camera/YOLO/PLC config (engineer only)

## Alerts
- Red: NG detected → check rejected part
- Yellow: System issue → check System Health panel

## Daily Ops
Start: Verify all green lights, OK Rate > 90%, PLC Connected
During: Monitor NG alerts, watch trend chart
End: Export CSV, note anomalies, verify backup

## Emergency

### NG Rate > 25%
1. Stop line 2. Check camera/lens/lighting 3. Check new part variant 4. Adjust threshold

### PLC Disconnect
1. Check cable 2. Ping: `docker exec yolo-edge ping 192.168.1.10` 3. Auto-reconnects 4. Verify PLC RUN mode

### Camera Failure
1. `v4l2-ctl --list-devices` 2. Restart: `docker compose restart inference-engine`
