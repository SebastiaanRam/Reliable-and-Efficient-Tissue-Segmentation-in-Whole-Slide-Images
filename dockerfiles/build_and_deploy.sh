#!/bin/bash

# Build and Deploy Script for Reliable and Efficient Tissue Segmentation
# This script builds the Docker image and pushes it to the registry

set -e  # Exit on any error

IMAGE_NAME="dockerdex.umcn.nl:5005/sebastiaanram/reliable-and-efficient-tissue-segmentation-in-whole-slide-images"

# Change to the root directory (parent of this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "=== Building Docker Image ==="
echo "Image name: $IMAGE_NAME"
echo "Build context: $(pwd)"
echo "Dockerfile: dockerfiles/Dockerfile"
echo ""

# Build the Docker image
echo "Starting Docker build..."
docker build -f dockerfiles/Dockerfile -t $IMAGE_NAME . --provenance=False

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✓ Docker build completed successfully!"
else
    echo "✗ Docker build failed!"
    exit 1
fi

echo ""
echo "=== Pushing to Registry ==="
echo "Pushing image to: $IMAGE_NAME"
echo ""

# Push the image to the registry
echo "Starting Docker push..."
docker push $IMAGE_NAME

# Check if push was successful
if [ $? -eq 0 ]; then
    echo "✓ Docker push completed successfully!"
    echo ""
    echo "=== Deployment Complete ==="
    echo "Image available at: $IMAGE_NAME"
    echo "Ready for use in SLURM jobs and containers"
else
    echo "✗ Docker push failed!"
    exit 1
fi
