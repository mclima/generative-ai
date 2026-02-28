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

print(f"Starting uvicorn on port {port}", flush=True)
print(f"PORT env variable: {os.environ.get('PORT', 'NOT SET')}", flush=True)
print(f"DATABASE_URL: {'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}", flush=True)
print(f"REDIS_URL: {'SET' if os.environ.get('REDIS_URL') else 'NOT SET'}", flush=True)
print(f"JWT_SECRET_KEY: {'SET' if os.environ.get('JWT_SECRET_KEY') else 'NOT SET'}", flush=True)
print(f"CORS_ORIGINS: {os.environ.get('CORS_ORIGINS', 'NOT SET')}", flush=True)

# Run uvicorn with the correct port
cmd = [
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", port,
    "--workers", "1",  # Use 1 worker for easier debugging
    "--log-level", "debug"
]

print(f"Running command: {' '.join(cmd)}", flush=True)
try:
    result = subprocess.call(cmd)
    print(f"Uvicorn exited with code: {result}", flush=True)
    sys.exit(result)
except Exception as e:
    print(f"ERROR starting uvicorn: {e}", flush=True)
    sys.exit(1)
