"""
News Service for retrieving and managing news articles with sentiment analysis.

This service provides caching, deduplication, and batch retrieval for news articles.
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib

from app.mcp.tools.news import NewsMCPTools, NewsArticle
from app.mcp.exceptions import MCPToolError, MCPConnectionError, MCPTimeoutError
from app.redis_client import get_redis
from app.services.sentiment_analyzer import SentimentAnalyzer, StockSentiment

logger = logging.getLogger(__name__)


class NewsService:
    """
    Service for retrieving news articles with caching and deduplication.
    
    Implements:
    - Redis caching with 15-minute TTL for news articles
    - News deduplication based on headline similarity
    - Batch news retrieval for multiple stocks
    """
    
    # Cache TTL in seconds
    NEWS_CACHE_TTL = 900  # 15 minutes for news articles
    
    def __init__(self, mcp_tools: NewsMCPTools, sentiment_analyzer: Optional[SentimentAnalyzer] = None):
        """
        Initialize News Service.
        
        Args:
            mcp_tools: NewsMCPTools instance for MCP communication
            sentiment_analyzer: Optional SentimentAnalyzer instance
        """
        self.mcp_tools = mcp_tools
        self.redis = get_redis()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
    
    def _get_stock_news_cache_key(self, ticker: str) -> str:
        """Get Redis cache key for stock news."""
        return f"stock:news:{ticker.upper()}"
    
    def _get_market_news_cache_key(self) -> str:
        """Get Redis cache key for market news."""
        return "market:news"
    
    def _calculate_article_hash(self, article: NewsArticle) -> str:
        """
        Calculate a hash for an article based on headline only.
        
        Used for deduplication - articles with same headline (case-insensitive)
        are considered duplicates regardless of source.
        
        Args:
            article: NewsArticle to hash
        
        Returns:
            Hash string
        """
        # Normalize headline for comparison (case-insensitive)
        normalized_headline = article.headline.lower().strip()
        return hashlib.md5(normalized_headline.encode()).hexdigest()
    
    def _deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Remove duplicate articles based on headline similarity.
        
        Args:
            articles: List of news articles
        
        Returns:
            Deduplicated list of articles
        """
        seen_hashes = set()
        deduplicated = []
        
        for article in articles:
            article_hash = self._calculate_article_hash(article)
            
            if article_hash not in seen_hashes:
                seen_hashes.add(article_hash)
                deduplicated.append(article)
            else:
                logger.debug(f"Duplicate article filtered: {article.headline}")
        
        logger.info(f"Deduplicated {len(articles)} articles to {len(deduplicated)}")
        return deduplicated
    
    async def getStockNews(self, ticker: str, limit: int = 10) -> List[NewsArticle]:
        """
        Get news for a specific stock with caching and deduplication.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of articles to return
        
        Returns:
            List of deduplicated news articles
        
        Raises:
            ValueError: If ticker is invalid or data cannot be retrieved
        """
        ticker = ticker.upper()
        cache_key = self._get_stock_news_cache_key(ticker)
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for stock news: {ticker}")
                data_list = json.loads(cached_data)
                articles = [NewsArticle(**item) for item in data_list]
                
                # Apply limit
                return articles[:limit]
        except Exception as e:
            logger.warning(f"Failed to read stock news from cache for {ticker}: {e}")
        
        # Fetch from MCP
        try:
            articles = await self.mcp_tools.get_stock_news(ticker, limit=limit * 2)
            
            # Deduplicate articles
            deduplicated_articles = self._deduplicate_articles(articles)
            
            # Apply limit after deduplication
            limited_articles = deduplicated_articles[:limit]
            
            # Cache the result
            try:
                data_list = [article.dict() for article in limited_articles]
                self.redis.setex(
                    cache_key,
                    self.NEWS_CACHE_TTL,
                    json.dumps(data_list, default=str)
                )
                logger.debug(f"Cached stock news for {ticker}")
            except Exception as e:
                logger.warning(f"Failed to cache stock news for {ticker}: {e}")
            
            return limited_articles
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting stock news for {ticker}: {e}")
            raise ValueError(f"Unable to retrieve news for {ticker}: {str(e)}")
    
    async def getBatchStockNews(self, tickers: List[str]) -> Dict[str, List[NewsArticle]]:
        """
        Get news for multiple stocks.
        
        Args:
            tickers: List of stock ticker symbols
        
        Returns:
            Dictionary mapping ticker to list of news articles
        """
        results = {}
        
        for ticker in tickers:
            try:
                articles = await self.getStockNews(ticker)
                results[ticker.upper()] = articles
            except Exception as e:
                logger.warning(f"Failed to get news for {ticker}: {e}")
                # Continue with other tickers, return empty list for failed ticker
                results[ticker.upper()] = []
        
        return results
    
    async def getMarketNews(self, limit: int = 20) -> List[NewsArticle]:
        """
        Get general market news with caching and deduplication.
        
        Args:
            limit: Maximum number of articles to return
        
        Returns:
            List of deduplicated news articles
        
        Raises:
            ValueError: If data cannot be retrieved
        """
        cache_key = self._get_market_news_cache_key()
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug("Cache hit for market news")
                data_list = json.loads(cached_data)
                articles = [NewsArticle(**item) for item in data_list]
                
                # Apply limit
                return articles[:limit]
        except Exception as e:
            logger.warning(f"Failed to read market news from cache: {e}")
        
        # Fetch from MCP
        try:
            articles = await self.mcp_tools.get_market_news(limit=limit * 2)
            
            # Deduplicate articles
            deduplicated_articles = self._deduplicate_articles(articles)
            
            # Apply limit after deduplication
            limited_articles = deduplicated_articles[:limit]
            
            # Cache the result
            try:
                data_list = [article.dict() for article in limited_articles]
                self.redis.setex(
                    cache_key,
                    self.NEWS_CACHE_TTL,
                    json.dumps(data_list, default=str)
                )
                logger.debug("Cached market news")
            except Exception as e:
                logger.warning(f"Failed to cache market news: {e}")
            
            return limited_articles
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting market news: {e}")
            raise ValueError(f"Unable to retrieve market news: {str(e)}")
    
    def invalidate_stock_news_cache(self, ticker: str) -> None:
        """
        Invalidate cached news data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
        """
        cache_key = self._get_stock_news_cache_key(ticker)
        try:
            self.redis.delete(cache_key)
            logger.info(f"Invalidated news cache for {ticker}")
        except Exception as e:
            logger.warning(f"Failed to invalidate news cache for {ticker}: {e}")
    
    def invalidate_market_news_cache(self) -> None:
        """Invalidate cached market news data."""
        cache_key = self._get_market_news_cache_key()
        try:
            self.redis.delete(cache_key)
            logger.info("Invalidated market news cache")
        except Exception as e:
            logger.warning(f"Failed to invalidate market news cache: {e}")

    async def getStockSentiment(self, ticker: str, limit: int = 10) -> StockSentiment:
        """
        Get aggregated sentiment for a stock based on recent news.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of articles to analyze
        
        Returns:
            StockSentiment with overall sentiment and article count
        
        Raises:
            ValueError: If ticker is invalid or data cannot be retrieved
        """
        # Get recent news articles
        articles = await self.getStockNews(ticker, limit=limit)
        
        # Analyze sentiment
        stock_sentiment = self.sentiment_analyzer.getStockSentiment(ticker, articles)
        
        return stock_sentiment
