#!/bin/bash

# VisionAssist YOLOv8 Setup Script
# This script automates the setup process for YOLOv8 model

set -e

echo "🚀 VisionAssist YOLOv8 Setup"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "📦 Installing ultralytics..."
pip3 install ultralytics

echo ""
echo "🔄 Exporting YOLOv8n model to TensorFlow.js format..."
python3 scripts/export-yolov8.py

echo ""
echo "📁 Copying model to public folder..."
if [ -d "yolov8n_web_model" ]; then
    cp -r yolov8n_web_model public/
    echo "✅ Model copied successfully!"
else
    echo "❌ Model export failed. yolov8n_web_model directory not found."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. npm install"
echo "2. npm run dev"
echo "3. Open http://localhost:3000"
echo ""
