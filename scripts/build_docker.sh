#!/bin/bash
# Script to build Docker image
# สคริปต์สำหรับ build Docker image

echo "Building YOLO Inspection System Docker image..."

cd "$(dirname "$0")/.."

# Build the image
docker-compose build yolo-inspection

echo ""
echo "✓ Build complete!"
echo ""
echo "To run the container:"
echo "  ./scripts/run_docker.sh"
echo ""
echo "To run with GPU:"
echo "  ./scripts/run_docker_gpu.sh"
