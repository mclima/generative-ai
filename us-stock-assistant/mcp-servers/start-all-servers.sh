#!/bin/bash

# Start all MCP servers
# This script starts all three MCP servers in the background

echo "Starting MCP Servers..."

# Check if virtual environments exist
for server in stock-data-server news-server market-data-server; do
    if [ ! -d "$server/venv" ]; then
        echo "Error: Virtual environment not found for $server"
        echo "Please run setup first:"
        echo "  cd $server && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
done

# Start stock data server
echo "Starting Stock Data Server on port 8001..."
cd stock-data-server
source venv/bin/activate
python main.py > ../logs/stock-data-server.log 2>&1 &
STOCK_PID=$!
cd ..

# Start news server
echo "Starting News Server on port 8002..."
cd news-server
source venv/bin/activate
python main.py > ../logs/news-server.log 2>&1 &
NEWS_PID=$!
cd ..

# Start market data server
echo "Starting Market Data Server on port 8003..."
cd market-data-server
source venv/bin/activate
python main.py > ../logs/market-data-server.log 2>&1 &
MARKET_PID=$!
cd ..

# Create logs directory if it doesn't exist
mkdir -p logs

# Save PIDs to file for stopping later
echo $STOCK_PID > logs/stock-data-server.pid
echo $NEWS_PID > logs/news-server.pid
echo $MARKET_PID > logs/market-data-server.pid

echo ""
echo "All servers started!"
echo "Stock Data Server: http://localhost:8001 (PID: $STOCK_PID)"
echo "News Server: http://localhost:8002 (PID: $NEWS_PID)"
echo "Market Data Server: http://localhost:8003 (PID: $MARKET_PID)"
echo ""
echo "Logs are in the logs/ directory"
echo "To stop all servers, run: ./stop-all-servers.sh"
