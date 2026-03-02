"""
MCP News Server using official Model Context Protocol
Provides stock news and market news via MCP tools
"""
from typing import Any
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("news-server")

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
POLYGON_BASE_URL = "https://api.polygon.io"


@mcp.tool()
async def get_stock_news(ticker: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    Get recent news articles for a specific stock.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        limit: Maximum number of articles to return (default: 10)
    
    Returns:
        List of news articles with headline, source, URL, published date, and summary
    """
    ticker = ticker.upper()
    
    async with httpx.AsyncClient() as client:
        url = f"{POLYGON_BASE_URL}/v2/reference/news"
        response = await client.get(
            url,
            params={
                "apiKey": POLYGON_API_KEY,
                "ticker": ticker,
                "limit": limit,
                "order": "desc"
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            return []
        
        articles = []
        for article in data.get("results", []):
            articles.append({
                "id": article.get("id", ""),
                "headline": article.get("title", ""),
                "source": article.get("publisher", {}).get("name", "Unknown"),
                "url": article.get("article_url", ""),
                "published_at": article.get("published_utc", ""),
                "summary": article.get("description", "")[:200] + "..." if len(article.get("description", "")) > 200 else article.get("description", "")
            })
        
        return articles


@mcp.tool()
async def get_market_news(limit: int = 20) -> list[dict[str, Any]]:
    """
    Get recent market-wide news articles.
    
    Args:
        limit: Maximum number of articles to return (default: 20)
    
    Returns:
        List of market news articles with headline, source, URL, published date, and summary
    """
    async with httpx.AsyncClient() as client:
        url = f"{POLYGON_BASE_URL}/v2/reference/news"
        response = await client.get(
            url,
            params={
                "apiKey": POLYGON_API_KEY,
                "limit": limit,
                "order": "desc"
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            return []
        
        articles = []
        for article in data.get("results", []):
            articles.append({
                "id": article.get("id", ""),
                "headline": article.get("title", ""),
                "source": article.get("publisher", {}).get("name", "Unknown"),
                "url": article.get("article_url", ""),
                "published_at": article.get("published_utc", ""),
                "summary": article.get("description", "")[:200] + "..." if len(article.get("description", "")) > 200 else article.get("description", "")
            })
        
        return articles


@mcp.tool()
async def get_trending_tickers(limit: int = 10) -> list[dict[str, Any]]:
    """
    Get trending stock tickers based on news mentions.
    
    Args:
        limit: Maximum number of tickers to return (default: 10)
    
    Returns:
        List of trending tickers with ticker symbol, company name, and news count
    """
    # Get recent market news
    async with httpx.AsyncClient() as client:
        url = f"{POLYGON_BASE_URL}/v2/reference/news"
        response = await client.get(
            url,
            params={
                "apiKey": POLYGON_API_KEY,
                "limit": 50,
                "order": "desc"
            },
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK":
            return []
        
        # Count ticker mentions
        ticker_counts = {}
        for article in data.get("results", []):
            for ticker_data in article.get("tickers", []):
                ticker = ticker_data
                if ticker not in ticker_counts:
                    ticker_counts[ticker] = {
                        "ticker": ticker,
                        "company_name": ticker,  # Polygon doesn't provide company name in news
                        "news_count": 0,
                        "reason": "High news volume"
                    }
                ticker_counts[ticker]["news_count"] += 1
        
        # Sort by news count and return top tickers
        trending = sorted(ticker_counts.values(), key=lambda x: x["news_count"], reverse=True)
        return trending[:limit]


if __name__ == "__main__":
    import sys
    import os
    
    # Check if running with HTTP transport (for Railway)
    port = int(os.getenv("PORT", "8002"))
    
    # Run with HTTP/SSE transport for production deployment
    # This allows the MCP server to be accessed over HTTP while using the MCP protocol
    mcp.run(transport="sse", port=port)
