"""
MCP News Server using Polygon.io API
Provides stock news and market news
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MCP News Server", version="1.0.0")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
POLYGON_BASE_URL = "https://api.polygon.io"


class StockNewsRequest(BaseModel):
    ticker: str
    limit: int = 10


class MarketNewsRequest(BaseModel):
    limit: int = 20


class TrendingTickersRequest(BaseModel):
    limit: int = 10


@app.get("/")
async def root():
    return {
        "service": "MCP News Server",
        "version": "1.0.0",
        "provider": "Polygon.io",
        "tools": [
            "get_stock_news",
            "get_market_news",
            "get_trending_tickers"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "MCP News Server"}


@app.post("/tools/get_stock_news")
async def get_stock_news(request: StockNewsRequest):
    """
    Get recent news articles for a specific stock.
    """
    ticker = request.ticker.upper()
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{POLYGON_BASE_URL}/v2/reference/news"
            response = await client.get(
                url,
                params={
                    "apiKey": POLYGON_API_KEY,
                    "ticker": ticker,
                    "limit": request.limit,
                    "order": "desc"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                return {"success": True, "data": []}
            
            articles = []
            for article in data.get("results", []):
                articles.append({
                    "id": article.get("id", ""),
                    "headline": article.get("title", ""),
                    "source": article.get("publisher", {}).get("name", "Unknown"),
                    "url": article.get("article_url", ""),
                    "publishedAt": article.get("published_utc", ""),
                    "summary": article.get("description", "")[:200] + "..." if len(article.get("description", "")) > 200 else article.get("description", "")
                })
            
            return {
                "success": True,
                "data": articles
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock news: {str(e)}")


@app.post("/tools/get_market_news")
async def get_market_news(request: MarketNewsRequest):
    """
    Get general market news articles.
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"{POLYGON_BASE_URL}/v2/reference/news"
            response = await client.get(
                url,
                params={
                    "apiKey": POLYGON_API_KEY,
                    "limit": request.limit,
                    "order": "desc"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                return {"success": True, "data": []}
            
            articles = []
            for article in data.get("results", []):
                articles.append({
                    "id": article.get("id", ""),
                    "headline": article.get("title", ""),
                    "source": article.get("publisher", {}).get("name", "Unknown"),
                    "url": article.get("article_url", ""),
                    "publishedAt": article.get("published_utc", ""),
                    "summary": article.get("description", "")[:200] + "..." if len(article.get("description", "")) > 200 else article.get("description", ""),
                    "tickers": article.get("tickers", [])
                })
            
            return {
                "success": True,
                "data": articles
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market news: {str(e)}")


@app.post("/tools/get_trending_tickers")
async def get_trending_tickers(request: TrendingTickersRequest):
    """
    Get trending tickers based on recent news volume.
    This aggregates tickers from recent news articles.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get recent news and count ticker mentions
            url = f"{POLYGON_BASE_URL}/v2/reference/news"
            response = await client.get(
                url,
                params={
                    "apiKey": POLYGON_API_KEY,
                    "limit": 100,  # Get more articles to analyze
                    "order": "desc"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                return {"success": True, "data": []}
            
            # Count ticker mentions
            ticker_counts = {}
            for article in data.get("results", []):
                for ticker in article.get("tickers", []):
                    ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
            
            # Sort by count and get top tickers
            sorted_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)
            top_tickers = sorted_tickers[:request.limit]
            
            # Get price data for trending tickers
            trending = []
            for ticker, news_count in top_tickers:
                try:
                    price_url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
                    price_response = await client.get(
                        price_url,
                        params={"apiKey": POLYGON_API_KEY}
                    )
                    
                    if price_response.status_code == 200:
                        price_data = price_response.json()
                        if price_data.get("status") == "OK" and price_data.get("results"):
                            result = price_data["results"][0]
                            close_price = result["c"]
                            open_price = result["o"]
                            change_percent = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0
                            
                            trending.append({
                                "ticker": ticker,
                                "companyName": ticker,  # Would need additional API call for full name
                                "price": close_price,
                                "changePercent": round(change_percent, 2),
                                "volume": result["v"],
                                "newsCount": news_count,
                                "reason": f"Mentioned in {news_count} recent articles"
                            })
                except Exception:
                    continue
            
            return {
                "success": True,
                "data": trending
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending tickers: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVER_PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
