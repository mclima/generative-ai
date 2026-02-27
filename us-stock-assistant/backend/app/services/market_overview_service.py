"""
Market Overview Service for aggregating market-wide data, news, and sentiment.

This service provides market overview data including headlines, sentiment,
trending tickers, indices, and sector performance.
"""
import logging
from typing import List, Optional
from datetime import datetime
import json

from pydantic import BaseModel

from app.mcp.tools.news import NewsMCPTools, NewsArticle, TrendingTicker
from app.mcp.tools.stock_data import StockDataMCPTools, MarketIndex, StockPrice
from app.mcp.tools.market_data import MarketDataMCPTools, SectorPerformance
from app.mcp.exceptions import MCPToolError, MCPConnectionError, MCPTimeoutError
from app.redis_client import get_redis
from app.services.sentiment_analyzer import SentimentAnalyzer, SentimentScore

logger = logging.getLogger(__name__)


class MarketOverview(BaseModel):
    """Complete market overview data."""
    headlines: List[NewsArticle]
    sentiment: SentimentScore
    trending_tickers: List[TrendingTicker]
    indices: List[MarketIndex]
    sector_heatmap: Optional[List[SectorPerformance]] = None
    last_updated: datetime


class MarketOverviewService:
    """
    Service for retrieving market overview data with caching.
    
    Implements:
    - Redis caching with 15-minute TTL for market overview
    - Aggregation of headlines, sentiment, trending tickers, and indices
    - Conditional sector heatmap based on user preferences
    """
    
    # Cache TTL in seconds
    MARKET_OVERVIEW_CACHE_TTL = 900  # 15 minutes
    
    def __init__(
        self,
        news_tools: NewsMCPTools,
        stock_tools: StockDataMCPTools,
        market_tools: MarketDataMCPTools,
        sentiment_analyzer: Optional[SentimentAnalyzer] = None
    ):
        """
        Initialize Market Overview Service.
        
        Args:
            news_tools: NewsMCPTools instance for news data
            stock_tools: StockDataMCPTools instance for stock data
            market_tools: MarketDataMCPTools instance for market data
            sentiment_analyzer: Optional SentimentAnalyzer instance
        """
        self.news_tools = news_tools
        self.stock_tools = stock_tools
        self.market_tools = market_tools
        self.redis = get_redis()
        self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
    
    def _get_market_overview_cache_key(self) -> str:
        """Get Redis cache key for market overview."""
        return "market:overview"
    
    async def getMarketOverview(
        self,
        include_sector_heatmap: bool = False
    ) -> MarketOverview:
        """
        Get complete market overview data.
        
        Aggregates headlines, sentiment, trending tickers, and indices.
        Optionally includes sector heatmap when advanced features are enabled.
        
        Args:
            include_sector_heatmap: Whether to include sector heatmap
        
        Returns:
            MarketOverview with all required components
        
        Raises:
            ValueError: If data cannot be retrieved
        """
        cache_key = self._get_market_overview_cache_key()
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug("Cache hit for market overview")
                data = json.loads(cached_data)
                overview = MarketOverview(**data)
                
                # If sector heatmap is requested but not in cache, fetch it
                if include_sector_heatmap and overview.sector_heatmap is None:
                    try:
                        overview.sector_heatmap = await self.getSectorPerformance()
                    except Exception as e:
                        logger.warning(f"Failed to get sector performance: {e}")
                
                return overview
        except Exception as e:
            logger.warning(f"Failed to read market overview from cache: {e}")
        
        # Fetch all components
        try:
            # Fetch headlines (top market news)
            headlines = await self.news_tools.get_market_news(limit=10)
            
            # Annotate each article with its individual sentiment
            for article in headlines:
                article.sentiment = self.sentiment_analyzer.analyzeSentiment(article)
            
            # Get market indices first (needed for sentiment calculation)
            indices = await self.getMarketIndices()
            
            # Calculate overall market sentiment from headlines with indices alignment
            sentiment = self._calculate_market_sentiment(headlines, indices)
            
            # Get trending tickers (non-fatal if unavailable)
            try:
                trending_tickers = await self.getTrendingTickers(limit=10)
            except Exception as e:
                logger.warning(f"Failed to get trending tickers, continuing without: {e}")
                trending_tickers = []
            
            # Get sector performance if requested
            sector_heatmap = None
            if include_sector_heatmap:
                try:
                    sector_heatmap = await self.getSectorPerformance()
                except Exception as e:
                    logger.warning(f"Failed to get sector performance: {e}")
            
            # Create market overview
            overview = MarketOverview(
                headlines=headlines,
                sentiment=sentiment,
                trending_tickers=trending_tickers,
                indices=indices,
                sector_heatmap=sector_heatmap,
                last_updated=datetime.utcnow()
            )
            
            # Cache the result (without sector heatmap to keep cache size small)
            try:
                cache_data = overview.dict()
                cache_data['sector_heatmap'] = None  # Don't cache sector heatmap
                self.redis.setex(
                    cache_key,
                    self.MARKET_OVERVIEW_CACHE_TTL,
                    json.dumps(cache_data, default=str)
                )
                logger.debug("Cached market overview")
            except Exception as e:
                logger.warning(f"Failed to cache market overview: {e}")
            
            return overview
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting market overview: {e}")
            raise ValueError(f"Unable to retrieve market overview: {str(e)}")
    
    def _calculate_market_sentiment(self, headlines: List[NewsArticle], indices: Optional[List[MarketIndex]] = None) -> SentimentScore:
        """
        Calculate overall market sentiment from headlines with market indices alignment.
        
        This enhanced calculation:
        1. Computes weighted average sentiment from news headlines
        2. Analyzes market indices movement to determine market direction
        3. Adjusts sentiment score when news and market indices align
        4. Boosts confidence when news sentiment matches market movement
        
        Args:
            headlines: List of market news articles
            indices: Optional list of market indices for alignment analysis
        
        Returns:
            SentimentScore with overall market sentiment (enhanced with indices alignment)
        """
        if not headlines:
            return SentimentScore(
                label="neutral",
                score=0.0,
                confidence=0.0
            )
        
        # Use already-set per-article sentiment, or analyze if not set
        sentiments = []
        for article in headlines:
            if article.sentiment and isinstance(article.sentiment, SentimentScore):
                sentiments.append(article.sentiment)
            else:
                sentiment = self.sentiment_analyzer.analyzeSentiment(article)
                article.sentiment = sentiment
                sentiments.append(sentiment)
        
        # Calculate weighted average score (weighted by confidence)
        total_weighted_score = sum(s.score * s.confidence for s in sentiments)
        total_confidence = sum(s.confidence for s in sentiments)
        
        if total_confidence > 0:
            avg_score = total_weighted_score / total_confidence
        else:
            avg_score = 0.0
        
        # Calculate overall confidence (average of individual confidences)
        avg_confidence = total_confidence / len(sentiments) if sentiments else 0.0
        
        # ENHANCEMENT: Incorporate market indices alignment
        if indices and len(indices) > 0:
            # Calculate average market movement from indices
            avg_market_change = sum(idx.change_percent for idx in indices) / len(indices)
            
            # Determine if news sentiment aligns with market movement
            # Both negative: alignment, Both positive: alignment, Mixed: no alignment
            news_direction = "positive" if avg_score > 0.1 else "negative" if avg_score < -0.1 else "neutral"
            market_direction = "positive" if avg_market_change > 0.1 else "negative" if avg_market_change < -0.1 else "neutral"
            
            alignment_strength = 0.0
            if news_direction == market_direction and news_direction != "neutral":
                # Strong alignment: news and market agree
                alignment_strength = min(abs(avg_score), abs(avg_market_change / 100)) * 2
                # Boost confidence when they align (up to 20% boost)
                confidence_boost = min(0.20, alignment_strength)
                avg_confidence = min(1.0, avg_confidence + confidence_boost)
                
                # Slightly adjust score towards market direction (subtle reinforcement)
                market_signal = avg_market_change / 100  # Convert percentage to -1 to 1 scale
                avg_score = avg_score * 0.85 + market_signal * 0.15
                
                logger.info(f"News-Market alignment detected: {news_direction} (boost: +{confidence_boost:.2f} confidence)")
            elif news_direction != "neutral" and market_direction != "neutral" and news_direction != market_direction:
                # Misalignment: news says one thing, market does another
                # Reduce confidence slightly (up to 10% reduction)
                confidence_penalty = min(0.10, abs(avg_score) * 0.5)
                avg_confidence = max(0.0, avg_confidence - confidence_penalty)
                logger.info(f"News-Market misalignment: news={news_direction}, market={market_direction} (penalty: -{confidence_penalty:.2f} confidence)")
        
        # Determine overall label based on adjusted score
        if avg_score > 0.1:
            overall_label = "positive"
        elif avg_score < -0.1:
            overall_label = "negative"
        else:
            overall_label = "neutral"
        
        logger.info(f"Market sentiment: {overall_label} (score={avg_score:.2f}, confidence={avg_confidence:.2f})")
        
        return SentimentScore(
            label=overall_label,
            score=avg_score,
            confidence=avg_confidence
        )
    
    async def getTrendingTickers(self, limit: int = 10) -> List[TrendingTicker]:
        """
        Get trending tickers based on trading volume, price movement, and news mentions.
        
        Uses MCP to retrieve trending tickers with volume and news data.
        
        Args:
            limit: Maximum number of tickers to return
        
        Returns:
            List of trending tickers
        
        Raises:
            ValueError: If data cannot be retrieved
        """
        try:
            # Get trending tickers from news MCP (based on news volume)
            trending = await self.news_tools.get_trending_tickers(limit=limit)
            
            logger.info(f"Retrieved {len(trending)} trending tickers")
            return trending
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting trending tickers: {e}")
            raise ValueError(f"Unable to retrieve trending tickers: {str(e)}")
    
    async def getSectorPerformance(self) -> List[SectorPerformance]:
        """
        Get sector performance data showing performance across market sectors.
        
        Returns:
            List of sector performance data
        
        Raises:
            ValueError: If data cannot be retrieved
        """
        try:
            sectors = await self.market_tools.get_sector_performance()
            
            logger.info(f"Retrieved performance data for {len(sectors)} sectors")
            return sectors
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting sector performance: {e}")
            raise ValueError(f"Unable to retrieve sector performance: {str(e)}")
    
    async def getMarketIndices(self) -> List[MarketIndex]:
        """
        Get major market indices (S&P 500, NASDAQ, DOW) with current values and changes.
        
        Returns:
            List of market indices
        
        Raises:
            ValueError: If data cannot be retrieved
        """
        try:
            indices = await self.stock_tools.get_market_indices()
            
            logger.info(f"Retrieved {len(indices)} market indices")
            return indices
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting market indices: {e}")
            raise ValueError(f"Unable to retrieve market indices: {str(e)}")
    
    def invalidate_market_overview_cache(self) -> None:
        """Invalidate cached market overview data."""
        cache_key = self._get_market_overview_cache_key()
        try:
            self.redis.delete(cache_key)
            logger.info("Invalidated market overview cache")
        except Exception as e:
            logger.warning(f"Failed to invalidate market overview cache: {e}")
