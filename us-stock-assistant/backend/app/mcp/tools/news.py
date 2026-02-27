"""News MCP Server tools wrapper."""

import logging
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.mcp.client import MCPClient
from app.mcp.exceptions import MCPToolError, MCPValidationError

logger = logging.getLogger(__name__)


class ArticleSentiment(BaseModel):
    """Sentiment score for a news article."""
    label: str
    score: float
    confidence: float


class NewsArticle(BaseModel):
    """News article data."""
    id: str
    headline: str
    source: str
    url: str
    published_at: datetime
    summary: str
    sentiment: Optional[ArticleSentiment] = None


class TrendingTicker(BaseModel):
    """Trending ticker data."""
    ticker: str
    company_name: str
    price: float = 0.0
    change_percent: float = 0.0
    volume: int = 0
    news_count: int
    reason: str


class NewsMCPTools:
    """
    Wrapper for News MCP Server tools.
    
    Provides methods for retrieving stock news, market news, and trending tickers.
    """
    
    def __init__(self, client: MCPClient):
        """
        Initialize News MCP Tools.
        
        Args:
            client: MCP client instance
        """
        self.client = client
    
    async def get_stock_news(self, ticker: str, limit: int = 10) -> List[NewsArticle]:
        """
        Get news for a specific stock.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of articles to return
        
        Returns:
            List of news articles
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_stock_news",
                {"ticker": ticker.upper(), "limit": limit}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get stock news for {ticker}: {response.error}",
                    details={"ticker": ticker, "error": response.error}
                )
            
            # Validate and parse response
            try:
                articles = []
                for item in response.data:
                    articles.append(NewsArticle(
                        id=item.get("id", ""),
                        headline=item.get("headline", ""),
                        source=item.get("source", ""),
                        url=item.get("url", ""),
                        published_at=item.get("published_at") or item.get("publishedAt", ""),
                        summary=item.get("summary", "")
                    ))
                return articles
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for stock news: {str(e)}",
                    details={"ticker": ticker, "data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting stock news for {ticker}: {e}")
            raise MCPToolError(
                f"Unexpected error getting stock news: {str(e)}",
                details={"ticker": ticker}
            )
    
    async def get_market_news(self, limit: int = 20) -> List[NewsArticle]:
        """
        Get general market news.
        
        Args:
            limit: Maximum number of articles to return
        
        Returns:
            List of news articles
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_market_news",
                {"limit": limit}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get market news: {response.error}",
                    details={"error": response.error}
                )
            
            # Validate and parse response
            try:
                articles = []
                for item in response.data:
                    articles.append(NewsArticle(
                        id=item.get("id", ""),
                        headline=item.get("headline", ""),
                        source=item.get("source", ""),
                        url=item.get("url", ""),
                        published_at=item.get("published_at") or item.get("publishedAt", ""),
                        summary=item.get("summary", "")
                    ))
                return articles
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for market news: {str(e)}",
                    details={"data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting market news: {e}")
            raise MCPToolError(
                f"Unexpected error getting market news: {str(e)}"
            )
    
    async def get_trending_tickers(self, limit: int = 10) -> List[TrendingTicker]:
        """
        Get trending tickers based on news volume.
        
        Args:
            limit: Maximum number of tickers to return
        
        Returns:
            List of trending tickers
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_trending_tickers",
                {"limit": limit}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get trending tickers: {response.error}",
                    details={"error": response.error}
                )
            
            # Validate and parse response
            try:
                tickers = []
                for item in response.data:
                    tickers.append(TrendingTicker(
                        ticker=item.get("ticker", ""),
                        company_name=item.get("company_name") or item.get("companyName", ""),
                        price=item.get("price") or 0.0,
                        change_percent=item.get("change_percent") or item.get("changePercent", 0.0),
                        volume=item.get("volume") or 0,
                        news_count=item.get("news_count") or item.get("newsCount", 0),
                        reason=item.get("reason", "")
                    ))
                return tickers
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for trending tickers: {str(e)}",
                    details={"data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting trending tickers: {e}")
            raise MCPToolError(
                f"Unexpected error getting trending tickers: {str(e)}"
            )
