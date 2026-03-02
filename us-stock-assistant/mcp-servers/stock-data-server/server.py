"""
MCP Stock Data Server using official Model Context Protocol
Provides stock price, historical data, company info, and financial metrics via MCP tools
"""
from typing import Any
import httpx
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("stock-data-server")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
POLYGON_BASE_URL = "https://api.polygon.io"

# In-memory cache for search results
SEARCH_CACHE: dict[str, dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


@mcp.tool()
async def get_stock_price(ticker: str) -> dict[str, Any]:
    """
    Get current stock price and daily change.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
    
    Returns:
        Stock price data with current price, change, change percent, volume, and timestamp
    """
    ticker = ticker.upper()
    
    async with httpx.AsyncClient() as client:
        # Get previous close
        prev_close_url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
        prev_response = await client.get(
            prev_close_url,
            params={"apiKey": POLYGON_API_KEY},
            timeout=30.0
        )
        prev_response.raise_for_status()
        prev_data = prev_response.json()
        
        if prev_data.get("status") not in ("OK", "DELAYED") or not prev_data.get("results"):
            raise ValueError(f"No data found for ticker {ticker}")
        
        result = prev_data["results"][0]
        close_price = result["c"]
        open_price = result["o"]
        volume = result["v"]
        
        # Calculate change
        change = close_price - open_price
        change_percent = (change / open_price) * 100 if open_price > 0 else 0
        
        return {
            "ticker": ticker,
            "price": close_price,
            "change": round(change, 2),
            "changePercent": round(change_percent, 2),
            "volume": volume,
            "timestamp": datetime.fromtimestamp(result["t"] / 1000).isoformat()
        }


@mcp.tool()
async def get_historical_data(
    ticker: str,
    start_date: str,
    end_date: str,
    timespan: str = "day"
) -> list[dict[str, Any]]:
    """
    Get historical price data for a stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        timespan: Time interval (minute, hour, day, week, month, quarter, year)
    
    Returns:
        List of historical price data with date, open, high, low, close, and volume
    """
    ticker = ticker.upper()
    
    async with httpx.AsyncClient() as client:
        url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/{timespan}/{start_date}/{end_date}"
        response = await client.get(
            url,
            params={
                "apiKey": POLYGON_API_KEY,
                "adjusted": "true",
                "sort": "asc"
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
            raise ValueError(f"No historical data found for {ticker}")
        
        historical_data = []
        for bar in data["results"]:
            historical_data.append({
                "date": datetime.fromtimestamp(bar["t"] / 1000).date().isoformat(),
                "open": bar["o"],
                "high": bar["h"],
                "low": bar["l"],
                "close": bar["c"],
                "volume": bar["v"]
            })
        
        return historical_data


@mcp.tool()
async def get_company_info(ticker: str) -> dict[str, Any]:
    """
    Get company information and details.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
    
    Returns:
        Company information including name, sector, industry, market cap, and description
    """
    ticker = ticker.upper()
    
    async with httpx.AsyncClient() as client:
        url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
        response = await client.get(
            url,
            params={"apiKey": POLYGON_API_KEY},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
            raise ValueError(f"No company info found for {ticker}")
        
        result = data["results"]
        
        return {
            "ticker": ticker,
            "name": result.get("name", ""),
            "sector": result.get("sic_description", ""),
            "industry": result.get("sic_description", ""),
            "marketCap": result.get("market_cap", 0),
            "description": result.get("description", "")
        }


@mcp.tool()
async def get_financial_metrics(ticker: str) -> dict[str, Any]:
    """
    Get financial metrics for a stock including 52-week high/low.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
    
    Returns:
        Financial metrics including 52-week high and low
    """
    ticker = ticker.upper()
    
    async with httpx.AsyncClient() as client:
        # Get ticker details
        url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
        response = await client.get(
            url,
            params={"apiKey": POLYGON_API_KEY},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
            raise ValueError(f"No metrics found for {ticker}")
        
        # Get recent price data for 52-week high/low calculation
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        hist_url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
        hist_response = await client.get(
            hist_url,
            params={"apiKey": POLYGON_API_KEY, "adjusted": "true"},
            timeout=30.0
        )
        
        fifty_two_week_high = None
        fifty_two_week_low = None
        
        if hist_response.status_code == 200:
            hist_data = hist_response.json()
            if hist_data.get("status") in ("OK", "DELAYED") and hist_data.get("results"):
                highs = [bar["h"] for bar in hist_data["results"]]
                lows = [bar["l"] for bar in hist_data["results"]]
                fifty_two_week_high = max(highs)
                fifty_two_week_low = min(lows)
        
        return {
            "ticker": ticker,
            "peRatio": None,
            "eps": None,
            "dividendYield": None,
            "beta": None,
            "fiftyTwoWeekHigh": fifty_two_week_high,
            "fiftyTwoWeekLow": fifty_two_week_low
        }


@mcp.tool()
async def search_stocks(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Search for stocks by ticker or company name.
    
    Args:
        query: Search query (ticker symbol or company name)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching stocks with ticker, company name, exchange, and relevance score
    """
    cache_key = f"{query.upper()}:{limit}"
    current_time = time.time()
    
    # Check cache
    if cache_key in SEARCH_CACHE:
        cached_entry = SEARCH_CACHE[cache_key]
        if current_time - cached_entry["timestamp"] < CACHE_TTL_SECONDS:
            return cached_entry["results"]
    
    # Cache miss - fetch from Polygon API
    async with httpx.AsyncClient() as client:
        url = f"{POLYGON_BASE_URL}/v3/reference/tickers"
        query_upper = query.upper()

        # Compute next prefix for range query
        next_prefix = query_upper[:-1] + chr(ord(query_upper[-1]) + 1) if query_upper else ""

        # Run ticker-prefix range search and full-text search in parallel
        ticker_resp, text_resp = await asyncio.gather(
            client.get(url, params={
                "apiKey": POLYGON_API_KEY,
                "ticker.gte": query_upper,
                "ticker.lt": next_prefix,
                "active": "true",
                "limit": limit,
                "market": "stocks",
                "sort": "ticker",
                "order": "asc"
            }, timeout=30.0),
            client.get(url, params={
                "apiKey": POLYGON_API_KEY,
                "search": query,
                "active": "true",
                "limit": limit,
                "market": "stocks"
            }, timeout=30.0)
        )

        seen = {}
        # Process ticker-prefix results first (higher priority)
        for resp in (ticker_resp, text_resp):
            if resp.status_code == 200:
                data = resp.json()
                for ticker_data in data.get("results", []):
                    t = ticker_data.get("ticker", "")
                    if t and t not in seen:
                        seen[t] = {
                            "ticker": t,
                            "companyName": ticker_data.get("name", ""),
                            "exchange": ticker_data.get("primary_exchange", ""),
                            "relevanceScore": 1.0
                        }

        results = list(seen.values())[:limit]
        
        # Store in cache
        SEARCH_CACHE[cache_key] = {
            "results": results,
            "timestamp": current_time
        }
        
        return results


@mcp.tool()
async def get_market_indices() -> list[dict[str, Any]]:
    """
    Get major market indices (S&P 500, NASDAQ, DOW).
    
    Returns:
        List of market indices with name, symbol, value, change, and change percent
    """
    indices = {
        "SPY": "S&P 500",      # S&P 500 ETF
        "QQQ": "NASDAQ",       # NASDAQ ETF
        "DIA": "DOW"           # DOW ETF
    }
    
    results = []
    
    async with httpx.AsyncClient() as client:
        for ticker, name in indices.items():
            try:
                url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
                response = await client.get(
                    url,
                    params={"apiKey": POLYGON_API_KEY},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") in ("OK", "DELAYED") and data.get("results"):
                        result = data["results"][0]
                        close_price = result["c"]
                        open_price = result["o"]
                        change = close_price - open_price
                        change_percent = (change / open_price) * 100 if open_price > 0 else 0
                        
                        results.append({
                            "name": name,
                            "symbol": ticker,
                            "value": close_price,
                            "change": round(change, 2),
                            "changePercent": round(change_percent, 2)
                        })
            except Exception:
                continue
    
    return results


if __name__ == "__main__":
    import sys
    import os
    
    # Check if running with HTTP transport (for Railway)
    port = int(os.getenv("PORT", "8001"))
    
    # Run with HTTP/SSE transport for production deployment
    mcp.run(transport="sse", port=port)
