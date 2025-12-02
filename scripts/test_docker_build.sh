#!/bin/bash
# Script to test Docker build with different Dockerfiles
# สคริปต์สำหรับทดสอบ build Docker ด้วย Dockerfile หลายแบบ

echo "==================================================================="
echo "  YOLO Inspection System - Docker Build Test"
echo "==================================================================="
echo ""

cd "$(dirname "$0")/.."

# Function to test build
test_build() {
    local dockerfile=$1
    local tag=$2

    echo "Testing build with: $dockerfile"
    echo "Tag: $tag"
    echo "-------------------------------------------------------------------"

    if docker build -f "$dockerfile" -t "$tag" . 2>&1 | tee build.log; then
        echo ""
        echo "✓ Build successful with $dockerfile!"
        echo "Image: $tag"
        return 0
    else
        echo ""
        echo "✗ Build failed with $dockerfile"
        return 1
    fi
}

# Test default Dockerfile
echo "[1/3] Testing default Dockerfile..."
echo ""
if test_build "Dockerfile" "yolo-inspection:test-default"; then
    echo ""
    echo "========================================="
    echo "✓ SUCCESS! Default Dockerfile works!"
    echo "========================================="
    echo ""
    echo "You can now use:"
    echo "  ./scripts/run_docker.sh"
    exit 0
fi

echo ""
echo "Default Dockerfile failed. Trying alternatives..."
echo ""

# Test Ubuntu-based Dockerfile
echo "[2/3] Testing Ubuntu-based Dockerfile..."
echo ""
if test_build "Dockerfile.ubuntu" "yolo-inspection:test-ubuntu"; then
    echo ""
    echo "========================================="
    echo "✓ SUCCESS! Ubuntu Dockerfile works!"
    echo "========================================="
    echo ""
    echo "To use this version:"
    echo "  1. Rename: mv Dockerfile Dockerfile.old"
    echo "  2. Use Ubuntu: mv Dockerfile.ubuntu Dockerfile"
    echo "  3. Build: ./scripts/build_docker.sh"
    exit 0
fi

echo ""
echo "Ubuntu Dockerfile failed. Trying minimal version..."
echo ""

# Test minimal Dockerfile
echo "[3/3] Testing minimal Dockerfile..."
echo ""
if test_build "Dockerfile.minimal" "yolo-inspection:test-minimal"; then
    echo ""
    echo "========================================="
    echo "✓ SUCCESS! Minimal Dockerfile works!"
    echo "========================================="
    echo ""
    echo "To use this version:"
    echo "  1. Rename: mv Dockerfile Dockerfile.old"
    echo "  2. Use minimal: mv Dockerfile.minimal Dockerfile"
    echo "  3. Build: ./scripts/build_docker.sh"
    exit 0
fi

echo ""
echo "========================================="
echo "✗ All Docker builds failed!"
echo "========================================="
echo ""
echo "Please check build.log for details"
echo ""
echo "Common solutions:"
echo "  1. Update Docker: sudo apt-get update && sudo apt-get upgrade docker-ce"
echo "  2. Clear cache: docker system prune -a"
echo "  3. Check internet connection"
echo "  4. Try building on different network"
echo ""

exit 1
