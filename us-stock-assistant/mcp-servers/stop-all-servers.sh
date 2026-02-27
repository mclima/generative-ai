#!/bin/bash

# Stop all MCP servers

echo "Stopping MCP Servers..."

# Check if PID files exist
if [ ! -d "logs" ]; then
    echo "No servers appear to be running (no logs directory found)"
    exit 0
fi

# Stop each server
for server in stock-data-server news-server market-data-server; do
    PID_FILE="logs/$server.pid"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $server (PID: $PID)..."
            kill $PID
            rm "$PID_FILE"
        else
            echo "$server is not running"
            rm "$PID_FILE"
        fi
    fi
done

echo "All servers stopped!"
