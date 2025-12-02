#!/bin/bash
# Script to run YOLO Inspection System in Docker
# สคริปต์สำหรับรัน YOLO Inspection System บน Docker

echo "==================================================================="
echo "  YOLO Inspection System - Docker Runner"
echo "  ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์ (Docker)"
echo "==================================================================="
echo ""

# Navigate to project directory
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running!"
    echo "Please start Docker and try again"
    exit 1
fi

# Set DISPLAY if not set
if [ -z "$DISPLAY" ]; then
    echo "[INFO] DISPLAY not set, setting to :0"
    export DISPLAY=:0
fi

echo "[1/5] Current DISPLAY: $DISPLAY"

# Allow X server connection
echo ""
echo "[2/5] Setting up X11 permissions..."
xhost +local:docker 2>/dev/null || echo "Warning: xhost command not found, GUI may not work"

# Clean old containers if exists
echo ""
echo "[3/5] Cleaning old containers..."
docker-compose down --remove-orphans 2>/dev/null || true
docker rm -f yolo_inspection_system 2>/dev/null || true

# Build the image if not exists
echo ""
echo "[4/5] Checking Docker image..."
if ! docker images | grep -q "yolo-inspection"; then
    echo "Image not found, building..."
    docker-compose build yolo-inspection
else
    echo "Image found, using existing image"
    echo "To rebuild: docker-compose build --no-cache"
fi

# Create necessary directories
echo ""
echo "[5/5] Creating necessary directories..."
mkdir -p data models reports logs config

# Run the container
echo ""
echo "========================================="
echo "Starting YOLO Inspection System..."
echo "========================================="
echo ""

# Export DISPLAY for docker-compose
export DISPLAY=${DISPLAY:-:0}
docker-compose up yolo-inspection

# Cleanup on exit
echo ""
echo "Cleaning up..."
xhost -local:docker 2>/dev/null || true

echo ""
echo "Done!"
