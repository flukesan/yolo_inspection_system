#!/bin/bash
# Clean Docker Script - ลบ containers/images เก่า
# ใช้เมื่อมีปัญหา ContainerConfig หรือ container conflict

echo "==================================================================="
echo "  Docker Clean Script"
echo "  ลบ containers และ images เก่าของ YOLO Inspection System"
echo "==================================================================="
echo ""

cd "$(dirname "$0")/.."

echo "[1/4] Stopping containers..."
docker-compose down --remove-orphans 2>/dev/null || true
docker stop $(docker ps -aq --filter name=yolo) 2>/dev/null || true

echo ""
echo "[2/4] Removing containers..."
docker rm -f $(docker ps -aq --filter name=yolo) 2>/dev/null || true
docker container prune -f

echo ""
echo "[3/4] Removing images..."
docker rmi -f $(docker images -q yolo-inspection) 2>/dev/null || true
docker rmi -f $(docker images -q yolo_inspection_system*) 2>/dev/null || true

echo ""
echo "[4/4] Cleaning up volumes and networks..."
docker volume prune -f
docker network prune -f

echo ""
echo "========================================="
echo "✓ Cleanup complete!"
echo "========================================="
echo ""
echo "Now you can build fresh:"
echo "  ./scripts/build_docker.sh"
echo ""
echo "Or run directly:"
echo "  ./scripts/run_docker.sh"
