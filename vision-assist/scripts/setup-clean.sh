#!/bin/bash

# VisionAssist YOLOv8 Setup Script with Clean Environment
# This script creates a virtual environment to avoid dependency conflicts

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

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv-yolo

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv-yolo/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies with correct versions
echo "📦 Installing dependencies (this may take a few minutes)..."
pip install --quiet 'numpy<2' 'tensorflow>=2.0.0,<=2.19.0' 'ultralytics>=8.0.0'

echo ""
echo "🔄 Exporting YOLOv8n model to TensorFlow.js format..."
python scripts/export-yolov8.py

# Deactivate virtual environment
deactivate

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
echo "Note: The virtual environment (.venv-yolo) can be deleted after setup."
echo "      It was only needed for model export."
echo ""
