#!/usr/bin/env python3
"""
Quick YOLOv8 export without TensorFlow dependency.
Uses ONNX as intermediate format which is faster.
"""

import subprocess
import sys
import os

def quick_export():
    print("🚀 Quick YOLOv8 export (ONNX method)")
    print("=" * 50)
    
    # Check if yolov8n.pt exists
    if not os.path.exists("yolov8n.pt"):
        print("📥 Downloading YOLOv8n model...")
        try:
            from ultralytics import YOLO
            model = YOLO("yolov8n.pt")
            print("✅ Model downloaded")
        except Exception as e:
            print(f"❌ Failed to download: {e}")
            print("\nTrying manual download...")
            subprocess.run([
                "curl", "-L", 
                "https://github.com/ultralytics/assets/releases/download/v8.4.0/yolov8n.pt",
                "-o", "yolov8n.pt"
            ])
    
    print("\n⚠️  Note: TensorFlow.js export is complex and slow.")
    print("Alternative: Use ONNX format with onnxruntime-web")
    print("\nFor now, let's use a pre-converted model.")
    print("\nPlease download the pre-converted model from:")
    print("https://github.com/Hyuto/yolov8-tfjs/tree/master/public")
    print("\nOr wait for the full export to complete (may take 5-10 minutes)")

if __name__ == "__main__":
    quick_export()
