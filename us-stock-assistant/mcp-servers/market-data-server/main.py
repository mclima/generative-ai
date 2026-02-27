"""
MCP Market Data Server using Polygon.io API
Provides sector performance and market sentiment data
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MCP Market Data Server", version="1.0.0")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
POLYGON_BASE_URL = "https://api.polygon.io"

# Sector ETFs for tracking sector performance
SECTOR_ETFS = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Energy": "XLE",
    "Consumer Discretionary": "XLY",
    "Industrials": "XLI",
    "Consumer Staples": "XLP",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
    "Communication Services": "XLC"
}


class SectorPerformanceRequest(BaseModel):
    pass


class MarketSentimentRequest(BaseModel):
    pass


@app.get("/")
async def root():
    return {
        "service": "MCP Market Data Server",
        "version": "1.0.0",
        "provider": "Polygon.io",
        "tools": [
            "get_sector_performance",
            "get_market_sentiment"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "service": "MCP Market Data Server"}


@app.post("/tools/get_sector_performance")
async def get_sector_performance(request: SectorPerformanceRequest):
    """
    Get performance data for market sectors using sector ETFs.
    """
    results = []
    
    try:
        async with httpx.AsyncClient() as client:
            for sector, etf_ticker in SECTOR_ETFS.items():
                try:
                    # Get previous close data
                    url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{etf_ticker}/prev"
                    response = await client.get(
                        url,
                        params={"apiKey": POLYGON_API_KEY}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "OK" and data.get("results"):
                            result = data["results"][0]
                            close_price = result["c"]
                            open_price = result["o"]
                            change_percent = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0
                            
                            # Get top/bottom performers (simplified - would need more data for real implementation)
                            results.append({
                                "sector": sector,
                                "changePercent": round(change_percent, 2),
                                "topPerformers": [],  # Would require additional API calls
                                "bottomPerformers": []  # Would require additional API calls
                            })
                except Exception:
                    continue
        
        # Sort by performance
        results.sort(key=lambda x: x["changePercent"], reverse=True)
        
        return {
            "success": True,
            "data": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sector performance: {str(e)}")


@app.post("/tools/get_market_sentiment")
async def get_market_sentiment(request: MarketSentimentRequest):
    """
    Get aggregated market sentiment based on major indices performance.
    This is a simplified sentiment calculation based on market movement.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get data for major indices
            indices = {
                "SPY": "S&P 500",
                "QQQ": "NASDAQ",
                "DIA": "DOW"
            }
            
            total_change = 0
            count = 0
            
            for ticker, name in indices.items():
                try:
                    url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
                    response = await client.get(
                        url,
                        params={"apiKey": POLYGON_API_KEY}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "OK" and data.get("results"):
                            result = data["results"][0]
                            close_price = result["c"]
                            open_price = result["o"]
                            change_percent = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0
                            total_change += change_percent
                            count += 1
                except Exception:
                    continue
            
            if count == 0:
                raise HTTPException(status_code=500, detail="Unable to calculate market sentiment")
            
            avg_change = total_change / count
            
            # Determine sentiment based on average change
            if avg_change > 1.0:
                sentiment = "bullish"
                sentiment_score = min(avg_change / 2, 1.0)  # Normalize to 0-1
            elif avg_change < -1.0:
                sentiment = "bearish"
                sentiment_score = max(avg_change / 2, -1.0)  # Normalize to -1-0
            else:
                sentiment = "neutral"
                sentiment_score = avg_change / 2
            
            return {
                "success": True,
                "data": {
                    "sentiment": sentiment,
                    "score": round(sentiment_score, 3),
                    "averageChange": round(avg_change, 2),
                    "description": f"Market is {sentiment} with average change of {avg_change:.2f}%"
                }
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating market sentiment: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    # Railway provides PORT env variable, fallback to 8003 for local development
    port = int(os.getenv("PORT", os.getenv("SERVER_PORT", 8003)))
    uvicorn.run(app, host="0.0.0.0", port=port)
