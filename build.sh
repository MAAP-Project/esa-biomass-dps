#!/bin/bash
set -euo pipefail

IMAGE_NAME="esa-biomass-dps"
IMAGE_TAG="latest"

echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"

docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

echo "Build complete: ${IMAGE_NAME}:${IMAGE_TAG}"
