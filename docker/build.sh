#!/bin/bash
set -euo pipefail
REGISTRY="${REGISTRY:-ghcr.io/flukesan}"
TAG="${TAG:-v2.0.0-beta}"
PLATFORMS="${PLATFORMS:-linux/amd64,linux/arm64}"
PUSH="${PUSH:-false}"
RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
while [[ $# -gt 0 ]]; do case "$1" in --push) PUSH="true"; shift ;; --platform) PLATFORMS="$2"; shift 2 ;; --tag) TAG="$2"; shift 2 ;; *) echo "Unknown: $1"; exit 1 ;; esac; done
if ! docker buildx version &>/dev/null; then echo "ERROR: docker buildx required"; exit 1; fi
if ! docker buildx inspect multiarch &>/dev/null; then docker buildx create --name multiarch --use; fi
docker buildx use multiarch
BUILD_ARGS="--platform ${PLATFORMS}"
[ "$PUSH" = "true" ] && BUILD_ARGS="$BUILD_ARGS --push" || BUILD_ARGS="$BUILD_ARGS --load"
echo "Building ${REGISTRY}/*:${TAG} for ${PLATFORMS}"
for svc in edge api frontend; do df="docker/Dockerfile.${svc}"; name="yolo-${svc}"; [ "$svc" = "frontend" ] && name="yolo-dashboard"; echo "  Building ${name}..."; docker buildx build $BUILD_ARGS -f "${df}" -t "${REGISTRY}/${name}:${TAG}" -t "${REGISTRY}/${name}:latest" . || echo "  WARN: ${name} build skipped"; done
echo "Build complete!"
