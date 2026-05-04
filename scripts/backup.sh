#!/bin/bash
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-/var/backups/yolo-inspection}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_CONTAINER="${DB_CONTAINER:-yolo-inspection-postgres-1}"
DB_NAME="${DB_NAME:-yolo_inspection}"
DB_USER="${DB_USER:-yolo}"
while [[ $# -gt 0 ]]; do case "$1" in --retention) RETENTION_DAYS="$2"; shift 2 ;; --dir) BACKUP_DIR="$2"; shift 2 ;; *) echo "Unknown: $1"; exit 1 ;; esac; done
mkdir -p "${BACKUP_DIR}/db"
echo "[$(date)] PostgreSQL backup..."
if docker exec "${DB_CONTAINER}" pg_dump -U "${DB_USER}" -Fc "${DB_NAME}" > "${BACKUP_DIR}/db/${DB_NAME}_${TIMESTAMP}.dump" 2>/dev/null; then echo "  OK: ${DB_NAME}_${TIMESTAMP}.dump"; else echo "  FAILED"; fi
echo "[$(date)] Cleaning old backups..."
find "${BACKUP_DIR}/db" -name "*.dump" -mtime "+${RETENTION_DAYS}" -delete 2>/dev/null || true
echo "Backup complete: ${BACKUP_DIR}"
