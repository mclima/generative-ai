"""
MCP Market Data Server using official Model Context Protocol
Provides sector performance and market sentiment data via MCP tools
"""
from typing import Any
import httpx
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("market-data-server")

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


@mcp.tool()
async def get_sector_performance() -> list[dict[str, Any]]:
    """
    Get performance data for market sectors using sector ETFs.
    
    Returns:
        List of sector performance data with sector name, change percent, and top/bottom performers
    """
    results = []
    
    async with httpx.AsyncClient() as client:
        for sector, etf_ticker in SECTOR_ETFS.items():
            try:
                # Get previous close data
                url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{etf_ticker}/prev"
                response = await client.get(
                    url,
                    params={"apiKey": POLYGON_API_KEY},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        result = data["results"][0]
                        close_price = result["c"]
                        open_price = result["o"]
                        change_percent = ((close_price - open_price) / open_price) * 100 if open_price > 0 else 0
                        
                        results.append({
                            "sector": sector,
                            "changePercent": round(change_percent, 2),
                            "topPerformers": [],
                            "bottomPerformers": []
                        })
            except Exception:
                continue
    
    # Sort by performance
    results.sort(key=lambda x: x["changePercent"], reverse=True)
    
    return results


@mcp.tool()
async def get_market_sentiment() -> dict[str, Any]:
    """
    Get aggregated market sentiment based on major indices performance.
    
    Returns:
        Market sentiment data with sentiment label, score, average change, and description
    """
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
                    params={"apiKey": POLYGON_API_KEY},
                    timeout=30.0
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
            raise ValueError("Unable to calculate market sentiment")
        
        avg_change = total_change / count
        
        # Determine sentiment based on average change
        if avg_change > 1.0:
            sentiment = "bullish"
            sentiment_score = min(avg_change / 2, 1.0)
        elif avg_change < -1.0:
            sentiment = "bearish"
            sentiment_score = max(avg_change / 2, -1.0)
        else:
            sentiment = "neutral"
            sentiment_score = avg_change / 2
        
        return {
            "sentiment": sentiment,
            "score": round(sentiment_score, 3),
            "averageChange": round(avg_change, 2),
            "description": f"Market is {sentiment} with average change of {avg_change:.2f}%"
        }


if __name__ == "__main__":
    import sys
    import os
    
    # Check if running with HTTP transport (for Railway)
    port = int(os.getenv("PORT", "8003"))
    
    # Run with HTTP/SSE transport for production deployment
    mcp.run(transport="sse", port=port)
