#!/bin/bash
# Script to run YOLO Inspection System in Docker with GPU support
# สคริปต์สำหรับรัน YOLO Inspection System บน Docker พร้อม GPU

echo "==================================================================="
echo "  YOLO Inspection System - Docker Runner (GPU)"
echo "  ระบบตรวจสอบคุณภาพชิ้นงานแบบเรียลไทม์ (Docker + GPU)"
echo "==================================================================="
echo ""

# Check NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "Warning: nvidia-smi not found. Make sure NVIDIA drivers are installed."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Allow X server connection
echo "[1/5] Setting up X11 permissions..."
xhost +local:docker

# Navigate to project directory
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running!"
    exit 1
fi

# Check NVIDIA Docker runtime
echo ""
echo "[2/5] Checking NVIDIA Docker runtime..."
if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA Docker runtime is available"
else
    echo "✗ NVIDIA Docker runtime not found!"
    echo "Please install nvidia-docker2:"
    echo "  https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi

# Build the image
echo ""
echo "[3/5] Building Docker image..."
docker-compose build yolo-inspection-gpu

# Create necessary directories
echo ""
echo "[4/5] Creating necessary directories..."
mkdir -p data models reports logs config

# Run the container with GPU
echo ""
echo "[5/5] Starting container with GPU..."
docker-compose --profile gpu up yolo-inspection-gpu

# Cleanup on exit
echo ""
echo "Cleaning up..."
xhost -local:docker

echo ""
echo "Done!"
