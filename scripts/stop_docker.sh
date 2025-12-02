#!/bin/bash
# Script to stop Docker containers
# สคริปต์สำหรับหยุด Docker containers

echo "Stopping YOLO Inspection System containers..."

cd "$(dirname "$0")/.."

# Stop all containers
docker-compose down

echo ""
echo "✓ Containers stopped!"
