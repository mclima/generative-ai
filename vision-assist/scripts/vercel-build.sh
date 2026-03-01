#!/bin/bash

# Vercel prebuild script for VisionAssist
# Downloads pre-converted YOLOv8n model files before build

set -e

echo "📦 Downloading YOLOv8n model files..."

# Create model directory
mkdir -p public/yolov8n_web_model

# Download model files from the yolov8-tfjs repository
cd public/yolov8n_web_model

echo "⬇️  Downloading model.json..."
curl -L -o model.json https://raw.githubusercontent.com/Hyuto/yolov8-tfjs/master/public/yolov8n_web_model/model.json

echo "⬇️  Downloading metadata.yaml..."
curl -L -o metadata.yaml https://raw.githubusercontent.com/Hyuto/yolov8-tfjs/master/public/yolov8n_web_model/metadata.yaml

echo "⬇️  Downloading model weights (4 shards)..."
curl -L -o group1-shard1of4.bin https://github.com/Hyuto/yolov8-tfjs/raw/master/public/yolov8n_web_model/group1-shard1of4.bin
curl -L -o group1-shard2of4.bin https://github.com/Hyuto/yolov8-tfjs/raw/master/public/yolov8n_web_model/group1-shard2of4.bin
curl -L -o group1-shard3of4.bin https://github.com/Hyuto/yolov8-tfjs/raw/master/public/yolov8n_web_model/group1-shard3of4.bin
curl -L -o group1-shard4of4.bin https://github.com/Hyuto/yolov8-tfjs/raw/master/public/yolov8n_web_model/group1-shard4of4.bin

cd ../..

echo "✅ Model files downloaded successfully!"
