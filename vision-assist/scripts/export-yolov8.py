#!/usr/bin/env python3
"""
Export YOLOv8 model to TensorFlow.js format for browser deployment.

Requirements:
    pip install ultralytics tensorflow

Usage:
    python scripts/export-yolov8.py
    
This will create a yolov8n_web_model directory with the TensorFlow.js model files.
Copy this directory to the public folder of your Next.js app.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies with proper versions."""
    print("📦 Checking dependencies...")
    
    dependencies = [
        "numpy<2",  # Fix NumPy compatibility
        "tensorflow>=2.0.0,<=2.19.0",
        "ultralytics"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", dep])
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to install {dep}, continuing anyway...")
    
    print("✅ Dependencies checked\n")

def export_yolov8():
    print("🚀 Starting YOLOv8 export to TensorFlow.js format...\n")
    
    # Install dependencies first
    install_dependencies()
    
    # Import after installation
    try:
        from ultralytics import YOLO
    except ImportError as e:
        print(f"❌ Error: Could not import ultralytics: {e}")
        print("\nPlease install manually:")
        print("  pip install numpy<2 tensorflow ultralytics")
        sys.exit(1)
    
    # Load YOLOv8n model (nano version - smallest and fastest)
    print("📦 Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")
    
    # Export to TensorFlow.js format
    print("🔄 Exporting to TensorFlow.js format...")
    try:
        model.export(format="tfjs")
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        print("\nTrying alternative approach...")
        print("Please install TensorFlow manually:")
        print("  pip install 'numpy<2' 'tensorflow>=2.0.0,<=2.19.0'")
        sys.exit(1)
    
    print("\n✅ Export complete!")
    print("\n📁 Next steps:")
    print("1. Copy the 'yolov8n_web_model' directory to your public folder:")
    print("   cp -r yolov8n_web_model public/")
    print("\n2. The model is now ready to use in your browser!")
    print("\n📊 Model info:")
    print("   - Model: YOLOv8n (nano)")
    print("   - Size: ~13 MB")
    print("   - Classes: 80 COCO objects")
    print("   - Expected FPS: 40-60 on modern devices")

if __name__ == "__main__":
    export_yolov8()
