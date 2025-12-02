#!/bin/bash
# Script to run YOLO Inspection System in Docker
# สคริปต์สำหรับรัน YOLO Inspection System บน Docker

echo "==================================================================="
echo "  YOLO Inspection System - Docker Runner"
echo "  ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์ (Docker)"
echo "==================================================================="
echo ""

# Allow X server connection
echo "[1/4] Setting up X11 permissions..."
xhost +local:docker

# Navigate to project directory
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running!"
    exit 1
fi

# Build the image
echo ""
echo "[2/4] Building Docker image..."
docker-compose build yolo-inspection

# Create necessary directories
echo ""
echo "[3/4] Creating necessary directories..."
mkdir -p data models reports logs config

# Run the container
echo ""
echo "[4/4] Starting container..."
docker-compose up yolo-inspection

# Cleanup on exit
echo ""
echo "Cleaning up..."
xhost -local:docker

echo ""
echo "Done!"
