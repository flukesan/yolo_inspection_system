#!/bin/bash
# Quick fix script for Docker build issues
# สคริปต์แก้ไขปัญหา Docker อย่างรวดเร็ว

echo "==================================================================="
echo "  Docker Build Quick Fix"
echo "==================================================================="
echo ""

cd "$(dirname "$0")/.."

# Fix 1: Remove problematic package from requirements.txt
echo "[1/3] Fixing requirements.txt..."
if grep -q "sqlite3-python" requirements.txt; then
    echo "  ✓ Found sqlite3-python, removing..."
    sed -i '/sqlite3-python/d' requirements.txt
    echo "  ✓ Fixed!"
else
    echo "  ✓ Already fixed"
fi

# Fix 2: Clear Docker cache
echo ""
echo "[2/3] Clearing Docker cache..."
docker system prune -f
echo "  ✓ Cache cleared"

# Fix 3: Try to build
echo ""
echo "[3/3] Building Docker image..."
echo ""

if docker build -t yolo-inspection:fixed . 2>&1 | tee build.log; then
    echo ""
    echo "========================================="
    echo "✓ BUILD SUCCESSFUL!"
    echo "========================================="
    echo ""
    echo "Image: yolo-inspection:fixed"
    echo ""
    echo "To run:"
    echo "  docker run -it --rm \\"
    echo "    -e DISPLAY=\$DISPLAY \\"
    echo "    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\"
    echo "    --device=/dev/video0:/dev/video0 \\"
    echo "    --network host \\"
    echo "    yolo-inspection:fixed"
    echo ""
    exit 0
else
    echo ""
    echo "========================================="
    echo "✗ BUILD FAILED"
    echo "========================================="
    echo ""
    echo "Check build.log for details"
    echo ""
    echo "Try alternative Dockerfiles:"
    echo "  docker build -f Dockerfile.ubuntu -t yolo-inspection ."
    echo "  docker build -f Dockerfile.lightweight -t yolo-inspection ."
    echo ""
    exit 1
fi
