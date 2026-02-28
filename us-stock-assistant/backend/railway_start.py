#!/usr/bin/env python3
"""
Railway startup wrapper for uvicorn
Handles PORT environment variable properly
"""
import os
import sys
import subprocess

# Get port from Railway's PORT env variable, default to 8000
port = os.environ.get("PORT", "8000")

print(f"Starting uvicorn on port {port}")
print(f"PORT env variable: {os.environ.get('PORT', 'NOT SET')}")

# Run uvicorn with the correct port
cmd = [
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", port,
    "--workers", "4"
]

print(f"Running command: {' '.join(cmd)}")
sys.exit(subprocess.call(cmd))
