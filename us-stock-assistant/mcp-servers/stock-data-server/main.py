"""
MCP Stock Data Server using Polygon.io API
Provides stock price, historical data, company info, and financial metrics
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

app = FastAPI(title="MCP Stock Data Server", version="1.0.0")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
POLYGON_BASE_URL = "https://api.polygon.io"

# In-memory cache for search results
# Format: {query: {"results": [...], "timestamp": float}}
SEARCH_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes


class StockPriceRequest(BaseModel):
    ticker: str


class HistoricalDataRequest(BaseModel):
    ticker: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    timespan: str = "day"  # minute, hour, day, week, month, quarter, year


class CompanyInfoRequest(BaseModel):
    ticker: str


class FinancialMetricsRequest(BaseModel):
    ticker: str


class SearchStocksRequest(BaseModel):
    query: str
    limit: int = 10


class MarketIndicesRequest(BaseModel):
    pass


@app.get("/")
async def root():
    return {
        "service": "MCP Stock Data Server",
        "version": "1.0.0",
        "provider": "Polygon.io",
        "tools": [
            "get_stock_price",
            "get_historical_data",
            "get_company_info",
            "get_financial_metrics",
            "search_stocks",
            "get_market_indices"
        ]
    }


@app.post("/tools/get_stock_price")
async def get_stock_price(request: StockPriceRequest):
    """
    Get current stock price and daily change.
    Uses Polygon's previous close and current snapshot.
    """
    ticker = request.ticker.upper()
    
    try:
        async with httpx.AsyncClient() as client:
            # Get previous close
            prev_close_url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
            prev_response = await client.get(
                prev_close_url,
                params={"apiKey": POLYGON_API_KEY}
            )
            prev_response.raise_for_status()
            prev_data = prev_response.json()
            
            if prev_data.get("status") not in ("OK", "DELAYED") or not prev_data.get("results"):
                raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
            
            result = prev_data["results"][0]
            close_price = result["c"]
            open_price = result["o"]
            volume = result["v"]
            
            # Calculate change
            change = close_price - open_price
            change_percent = (change / open_price) * 100 if open_price > 0 else 0
            
            return {
                "success": True,
                "data": {
                    "ticker": ticker,
                    "price": close_price,
                    "change": round(change, 2),
                    "changePercent": round(change_percent, 2),
                    "volume": volume,
                    "timestamp": datetime.fromtimestamp(result["t"] / 1000).isoformat()
                }
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock price: {str(e)}")


@app.post("/tools/get_historical_data")
async def get_historical_data(request: HistoricalDataRequest):
    """
    Get historical price data for a stock.
    """
    ticker = request.ticker.upper()
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/{request.timespan}/{request.start_date}/{request.end_date}"
            response = await client.get(
                url,
                params={
                    "apiKey": POLYGON_API_KEY,
                    "adjusted": "true",
                    "sort": "asc"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
                raise HTTPException(status_code=404, detail=f"No historical data found for {ticker}")
            
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
            
            return {
                "success": True,
                "data": historical_data
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


@app.post("/tools/get_company_info")
async def get_company_info(request: CompanyInfoRequest):
    """
    Get company information and details.
    """
    ticker = request.ticker.upper()
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
            response = await client.get(
                url,
                params={"apiKey": POLYGON_API_KEY}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
                raise HTTPException(status_code=404, detail=f"No company info found for {ticker}")
            
            result = data["results"]
            
            return {
                "success": True,
                "data": {
                    "ticker": ticker,
                    "name": result.get("name", ""),
                    "sector": result.get("sic_description", ""),
                    "industry": result.get("sic_description", ""),
                    "marketCap": result.get("market_cap", 0),
                    "description": result.get("description", "")
                }
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company info: {str(e)}")


@app.post("/tools/get_financial_metrics")
async def get_financial_metrics(request: FinancialMetricsRequest):
    """
    Get financial metrics for a stock.
    Note: Some metrics may require paid Polygon tier.
    """
    ticker = request.ticker.upper()
    
    try:
        async with httpx.AsyncClient() as client:
            # Get ticker details which includes some financial info
            url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
            response = await client.get(
                url,
                params={"apiKey": POLYGON_API_KEY}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") not in ("OK", "DELAYED") or not data.get("results"):
                raise HTTPException(status_code=404, detail=f"No metrics found for {ticker}")
            
            result = data["results"]
            
            # Get recent price data for 52-week high/low calculation
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            hist_url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
            hist_response = await client.get(
                hist_url,
                params={"apiKey": POLYGON_API_KEY, "adjusted": "true"}
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
                "success": True,
                "data": {
                    "ticker": ticker,
                    "peRatio": None,
                    "eps": None,
                    "dividendYield": None,
                    "beta": None,
                    "fiftyTwoWeekHigh": fifty_two_week_high,
                    "fiftyTwoWeekLow": fifty_two_week_low
                }
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching financial metrics: {str(e)}")


@app.post("/tools/search_stocks")
async def search_stocks(request: SearchStocksRequest):
    """
    Search for stocks by ticker or company name.
    Uses in-memory cache to reduce API calls.
    """
    cache_key = f"{request.query.upper()}:{request.limit}"
    current_time = time.time()
    
    # Check cache
    if cache_key in SEARCH_CACHE:
        cached_entry = SEARCH_CACHE[cache_key]
        if current_time - cached_entry["timestamp"] < CACHE_TTL_SECONDS:
            # Cache hit - return cached results
            return {
                "success": True,
                "data": cached_entry["results"]
            }
    
    # Cache miss - fetch from Polygon API
    try:
        async with httpx.AsyncClient() as client:
            url = f"{POLYGON_BASE_URL}/v3/reference/tickers"
            query_upper = request.query.upper()

            # Compute next prefix for range query (e.g. "NV" -> "NW")
            next_prefix = query_upper[:-1] + chr(ord(query_upper[-1]) + 1) if query_upper else ""

            # Run ticker-prefix range search and full-text search in parallel
            ticker_resp, text_resp = await asyncio.gather(
                client.get(url, params={
                    "apiKey": POLYGON_API_KEY,
                    "ticker.gte": query_upper,
                    "ticker.lt": next_prefix,
                    "active": "true",
                    "limit": request.limit,
                    "market": "stocks",
                    "sort": "ticker",
                    "order": "asc"
                }),
                client.get(url, params={
                    "apiKey": POLYGON_API_KEY,
                    "search": request.query,
                    "active": "true",
                    "limit": request.limit,
                    "market": "stocks"
                })
            )

            seen = {}
            # Process ticker-prefix results first (higher priority)
            for idx, resp in enumerate((ticker_resp, text_resp)):
                if resp.status_code == 200:
                    data = resp.json()
                    search_type = "prefix" if idx == 0 else "text"
                    print(f"[DEBUG] {search_type} search for '{request.query}': {len(data.get('results', []))} results")
                    for ticker_data in data.get("results", []):
                        t = ticker_data.get("ticker", "")
                        if t and t not in seen:
                            seen[t] = {
                                "ticker": t,
                                "companyName": ticker_data.get("name", ""),
                                "exchange": ticker_data.get("primary_exchange", ""),
                                "relevanceScore": 1.0
                            }
                else:
                    search_type = "prefix" if idx == 0 else "text"
                    print(f"[DEBUG] {search_type} search for '{request.query}' failed: {resp.status_code}")

            results = list(seen.values())[:request.limit]
            print(f"[DEBUG] Total unique results for '{request.query}': {len(results)}")
            
            # Store in cache
            SEARCH_CACHE[cache_key] = {
                "results": results,
                "timestamp": current_time
            }
            
            return {
                "success": True,
                "data": results
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching stocks: {str(e)}")


@app.post("/tools/get_market_indices")
async def get_market_indices(request: MarketIndicesRequest):
    """
    Get major market indices (S&P 500, NASDAQ, DOW).
    """
    indices = {
        "SPY": "S&P 500",      # S&P 500 ETF
        "QQQ": "NASDAQ",       # NASDAQ ETF
        "DIA": "DOW"           # DOW ETF
    }
    
    results = []
    
    try:
        async with httpx.AsyncClient() as client:
            for ticker, name in indices.items():
                try:
                    url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
                    response = await client.get(
                        url,
                        params={"apiKey": POLYGON_API_KEY}
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
        
        return {
            "success": True,
            "data": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market indices: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVER_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
