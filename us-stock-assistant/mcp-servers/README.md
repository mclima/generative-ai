# MCP Servers for US Stock Assistant

These are Model Context Protocol (MCP) servers that provide stock data, news, and market information using the Polygon.io API.

## Prerequisites

1. **Polygon.io API Key** (Free Tier)
   - Sign up at [polygon.io](https://polygon.io/)
   - Get your API key from the dashboard
   - Free tier: 5 API calls/minute, 2 years of historical data

2. **Python 3.11+**

## Setup Instructions

### 1. Set up each server

For each server (stock-data-server, news-server, market-data-server):

```bash
# Navigate to server directory
cd stock-data-server  # or news-server, or market-data-server

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your Polygon API key
# POLYGON_API_KEY=your-actual-api-key-here
```

### 2. Run the servers locally

Open three terminal windows and start each server:

**Terminal 1 - Stock Data Server:**

```bash
cd mcp-servers/stock-data-server
source venv/bin/activate
python3 main.py
# Server will run on http://localhost:8001
```

**Terminal 2 - News Server:**

```bash
cd mcp-servers/news-server
source venv/bin/activate
python3 main.py
# Server will run on http://localhost:8002
```

**Terminal 3 - Market Data Server:**

```bash
cd mcp-servers/market-data-server
source venv/bin/activate
python3 main.py
# Server will run on http://localhost:8003
```

### 3. Update your backend .env file

In your `backend/.env` file, add:

```bash
# MCP Servers
MCP_STOCK_DATA_URL=http://localhost:8001
MCP_NEWS_URL=http://localhost:8002
MCP_MARKET_DATA_URL=http://localhost:8003
```

## Testing the Servers

You can test each server by visiting:

- http://localhost:8001 - Stock Data Server
- http://localhost:8002 - News Server
- http://localhost:8003 - Market Data Server

Or use curl:

```bash
# Test stock price
curl -X POST http://localhost:8001/tools/get_stock_price \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# Test stock news
curl -X POST http://localhost:8002/tools/get_stock_news \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "limit": 5}'

# Test sector performance
curl -X POST http://localhost:8003/tools/get_sector_performance \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Available Tools

### Stock Data Server (Port 8001)

- `get_stock_price` - Get current stock price and daily change
- `get_historical_data` - Get historical price data
- `get_company_info` - Get company information
- `get_financial_metrics` - Get financial metrics (limited on free tier)
- `search_stocks` - Search for stocks by ticker or name
- `get_market_indices` - Get major market indices (S&P 500, NASDAQ, DOW)

### News Server (Port 8002)

- `get_stock_news` - Get recent news for a specific stock
- `get_market_news` - Get general market news
- `get_trending_tickers` - Get trending tickers based on news volume

### Market Data Server (Port 8003)

- `get_sector_performance` - Get performance data for market sectors
- `get_market_sentiment` - Get aggregated market sentiment

## Rate Limits

Polygon.io free tier allows:

- **5 API calls per minute**
- 2 years of historical data
- Real-time data delayed by 15 minutes

Be mindful of these limits when testing. The servers don't implement rate limiting themselves, so you'll need to manage this in your application.

## Production Deployment

For production use, consider:

1. **Upgrading to Polygon.io paid tier** for higher rate limits and real-time data
2. **Implementing caching** in your backend to reduce API calls
3. **Adding rate limiting** to the MCP servers
4. **Deploying servers** to a cloud platform (AWS, Google Cloud, etc.)
5. **Using environment-specific configurations**

## Troubleshooting

**"Invalid API key" error:**

- Make sure you've copied your API key correctly to the `.env` file
- Verify your API key is active on polygon.io dashboard

**"Rate limit exceeded" error:**

- You've exceeded 5 calls/minute on the free tier
- Wait a minute before making more requests
- Consider implementing caching in your backend

**"No data found" error:**

- The ticker symbol might be invalid
- The market might be closed (Polygon provides delayed data)
- Try a well-known ticker like "AAPL" or "MSFT"

## Alternative: Using Docker

You can also run all servers using Docker Compose (create a docker-compose.yml):

```yaml
version: "3.8"

services:
  stock-data-server:
    build: ./stock-data-server
    ports:
      - "8001:8001"
    environment:
      - POLYGON_API_KEY=${POLYGON_API_KEY}
      - SERVER_PORT=8001

  news-server:
    build: ./news-server
    ports:
      - "8002:8002"
    environment:
      - POLYGON_API_KEY=${POLYGON_API_KEY}
      - SERVER_PORT=8002

  market-data-server:
    build: ./market-data-server
    ports:
      - "8003:8003"
    environment:
      - POLYGON_API_KEY=${POLYGON_API_KEY}
      - SERVER_PORT=8003
```

Then run: `docker-compose up`
