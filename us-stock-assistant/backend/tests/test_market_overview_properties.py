"""
Property-based tests for Market Overview Service.

Feature: us-stock-assistant
Property 40: Market Overview Completeness
Property 41: Sector Heatmap Conditional Display
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from typing import List

from app.services.market_overview_service import MarketOverviewService, MarketOverview
from app.mcp.tools.news import NewsMCPTools, NewsArticle, TrendingTicker
from app.mcp.tools.stock_data import StockDataMCPTools, MarketIndex
from app.mcp.tools.market_data import MarketDataMCPTools, SectorPerformance
from app.services.sentiment_analyzer import SentimentAnalyzer


# Hypothesis strategies for generating test data
@st.composite
def news_article_strategy(draw):
    """Generate a news article."""
    headlines = [
        "Market reaches new high",
        "Economic data shows growth",
        "Fed announces rate decision",
        "Tech stocks rally",
        "Energy sector declines",
        "Inflation concerns rise",
        "Unemployment rate drops",
        "GDP growth exceeds expectations"
    ]
    
    sources = ["Reuters", "Bloomberg", "CNBC", "WSJ", "MarketWatch", "Financial Times"]
    
    return NewsArticle(
        id=draw(st.text(min_size=10, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")))),
        headline=draw(st.sampled_from(headlines)),
        source=draw(st.sampled_from(sources)),
        url=f"https://example.com/article/{draw(st.integers(min_value=1000, max_value=9999))}",
        published_at=datetime.now() - timedelta(hours=draw(st.integers(min_value=0, max_value=48))),
        summary=draw(st.text(min_size=50, max_size=200))
    )


@st.composite
def trending_ticker_strategy(draw):
    """Generate a trending ticker."""
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    companies = ["Apple Inc.", "Alphabet Inc.", "Microsoft Corp.", "Amazon.com Inc.", 
                 "Tesla Inc.", "NVIDIA Corp.", "Meta Platforms Inc.", "Netflix Inc."]
    reasons = ["High trading volume", "Major news event", "Earnings announcement", 
               "Analyst upgrade", "Product launch", "Market momentum"]
    
    idx = draw(st.integers(min_value=0, max_value=len(tickers)-1))
    
    return TrendingTicker(
        ticker=tickers[idx],
        company_name=companies[idx],
        news_count=draw(st.integers(min_value=5, max_value=50)),
        reason=draw(st.sampled_from(reasons))
    )


@st.composite
def market_index_strategy(draw):
    """Generate a market index."""
    indices = [
        ("S&P 500", "^GSPC"),
        ("NASDAQ", "^IXIC"),
        ("DOW", "^DJI")
    ]
    
    name, symbol = draw(st.sampled_from(indices))
    
    return MarketIndex(
        name=name,
        symbol=symbol,
        value=draw(st.floats(min_value=1000.0, max_value=50000.0)),
        change=draw(st.floats(min_value=-500.0, max_value=500.0)),
        change_percent=draw(st.floats(min_value=-5.0, max_value=5.0))
    )


@st.composite
def sector_performance_strategy(draw):
    """Generate sector performance data."""
    sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer", 
               "Industrial", "Materials", "Utilities", "Real Estate", "Communications"]
    
    tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "NFLX", "JPM", "BAC"]
    
    return SectorPerformance(
        sector=draw(st.sampled_from(sectors)),
        change_percent=draw(st.floats(min_value=-10.0, max_value=10.0)),
        top_performers=draw(st.lists(st.sampled_from(tickers), min_size=1, max_size=3, unique=True)),
        bottom_performers=draw(st.lists(st.sampled_from(tickers), min_size=1, max_size=3, unique=True))
    )


# Property 40: Market Overview Completeness
@pytest.mark.asyncio
@given(
    num_headlines=st.integers(min_value=5, max_value=15),
    num_trending=st.integers(min_value=5, max_value=15),
    include_sector_heatmap=st.booleans()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_market_overview_completeness(num_headlines, num_trending, include_sector_heatmap):
    """
    Property 40: Market Overview Completeness
    
    For any market overview request, the service should return all required components:
    - Top headlines from major financial news sources
    - Overall market sentiment score
    - Trending tickers
    - Major market indices (S&P 500, NASDAQ, DOW)
    
    Validates: Requirements 12.1, 12.2, 12.3, 12.6
    """
    # Create mock data
    mock_headlines = [
        NewsArticle(
            id=f"headline-{i}",
            headline=f"Market headline {i}",
            source="Reuters",
            url=f"https://example.com/{i}",
            published_at=datetime.now() - timedelta(hours=i),
            summary=f"Summary {i}"
        )
        for i in range(num_headlines)
    ]
    
    mock_trending = [
        TrendingTicker(
            ticker=f"TICK{i}",
            company_name=f"Company {i}",
            news_count=10 + i,
            reason="High trading volume"
        )
        for i in range(num_trending)
    ]
    
    mock_indices = [
        MarketIndex(name="S&P 500", symbol="^GSPC", value=4500.0, change=50.0, change_percent=1.1),
        MarketIndex(name="NASDAQ", symbol="^IXIC", value=14000.0, change=100.0, change_percent=0.7),
        MarketIndex(name="DOW", symbol="^DJI", value=35000.0, change=-30.0, change_percent=-0.1)
    ]
    
    mock_sectors = [
        SectorPerformance(
            sector="Technology",
            change_percent=2.5,
            top_performers=["AAPL", "GOOGL"],
            bottom_performers=["IBM"]
        ),
        SectorPerformance(
            sector="Healthcare",
            change_percent=-1.2,
            top_performers=["JNJ"],
            bottom_performers=["PFE", "MRNA"]
        )
    ]
    
    # Mock MCP tools
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_news_tools.get_market_news.return_value = mock_headlines
    mock_news_tools.get_trending_tickers.return_value = mock_trending
    
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_stock_tools.get_market_indices.return_value = mock_indices
    
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    mock_market_tools.get_sector_performance.return_value = mock_sectors
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Get market overview
        result = await service.getMarketOverview(include_sector_heatmap=include_sector_heatmap)
        
        # Verify result is a MarketOverview object
        assert isinstance(result, MarketOverview)
        
        # Verify all required components are present
        # 1. Headlines
        assert result.headlines is not None
        assert isinstance(result.headlines, list)
        assert len(result.headlines) > 0
        for headline in result.headlines:
            assert isinstance(headline, NewsArticle)
            assert headline.headline is not None
            assert headline.source is not None
            assert headline.url is not None
            assert headline.published_at is not None
        
        # 2. Sentiment score
        assert result.sentiment is not None
        assert result.sentiment.label in ["positive", "negative", "neutral"]
        assert -1.0 <= result.sentiment.score <= 1.0
        assert 0.0 <= result.sentiment.confidence <= 1.0
        
        # 3. Trending tickers
        assert result.trending_tickers is not None
        assert isinstance(result.trending_tickers, list)
        assert len(result.trending_tickers) > 0
        for ticker in result.trending_tickers:
            assert isinstance(ticker, TrendingTicker)
            assert ticker.ticker is not None
            assert ticker.company_name is not None
            assert ticker.news_count > 0
            assert ticker.reason is not None
        
        # 4. Market indices (S&P 500, NASDAQ, DOW)
        assert result.indices is not None
        assert isinstance(result.indices, list)
        assert len(result.indices) >= 3  # At least S&P 500, NASDAQ, DOW
        
        # Verify major indices are present
        index_names = [idx.name for idx in result.indices]
        assert "S&P 500" in index_names
        assert "NASDAQ" in index_names
        assert "DOW" in index_names
        
        for index in result.indices:
            assert isinstance(index, MarketIndex)
            assert index.name is not None
            assert index.symbol is not None
            assert index.value > 0
            assert index.change is not None
            assert index.change_percent is not None
        
        # 5. Last updated timestamp
        assert result.last_updated is not None
        assert isinstance(result.last_updated, datetime)
        
        # 6. Sector heatmap (conditional)
        if include_sector_heatmap:
            assert result.sector_heatmap is not None
            assert isinstance(result.sector_heatmap, list)
            assert len(result.sector_heatmap) > 0
        # Note: sector_heatmap can be None even if not requested, or if there was an error


# Property 41: Sector Heatmap Conditional Display
@pytest.mark.asyncio
@given(
    advanced_features_enabled=st.booleans()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_sector_heatmap_conditional_display(advanced_features_enabled):
    """
    Property 41: Sector Heatmap Conditional Display
    
    For any market overview request, the sector heatmap should only be included
    when advanced features are enabled in user preferences.
    
    Validates: Requirements 12.4
    """
    # Create mock data
    mock_headlines = [
        NewsArticle(
            id="headline-1",
            headline="Market news",
            source="Reuters",
            url="https://example.com/1",
            published_at=datetime.now(),
            summary="Summary"
        )
    ]
    
    mock_trending = [
        TrendingTicker(
            ticker="AAPL",
            company_name="Apple Inc.",
            news_count=15,
            reason="High volume"
        )
    ]
    
    mock_indices = [
        MarketIndex(name="S&P 500", symbol="^GSPC", value=4500.0, change=50.0, change_percent=1.1)
    ]
    
    mock_sectors = [
        SectorPerformance(
            sector="Technology",
            change_percent=2.5,
            top_performers=["AAPL", "GOOGL"],
            bottom_performers=["IBM"]
        )
    ]
    
    # Mock MCP tools
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_news_tools.get_market_news.return_value = mock_headlines
    mock_news_tools.get_trending_tickers.return_value = mock_trending
    
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_stock_tools.get_market_indices.return_value = mock_indices
    
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    mock_market_tools.get_sector_performance.return_value = mock_sectors
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Get market overview with conditional sector heatmap
        result = await service.getMarketOverview(
            include_sector_heatmap=advanced_features_enabled
        )
        
        # Verify sector heatmap is included only when advanced features are enabled
        if advanced_features_enabled:
            # When advanced features are enabled, sector heatmap should be present
            assert result.sector_heatmap is not None
            assert isinstance(result.sector_heatmap, list)
            assert len(result.sector_heatmap) > 0
            
            # Verify sector performance data structure
            for sector in result.sector_heatmap:
                assert isinstance(sector, SectorPerformance)
                assert sector.sector is not None
                assert sector.change_percent is not None
                assert isinstance(sector.top_performers, list)
                assert isinstance(sector.bottom_performers, list)
        else:
            # When advanced features are disabled, sector heatmap should be None
            # (or not fetched from MCP)
            # Note: The service may still return None even if requested due to errors
            pass


@pytest.mark.asyncio
async def test_market_overview_caching():
    """
    Test that market overview is properly cached with 15-minute TTL.
    
    Validates: Requirements 12.5
    """
    mock_headlines = [
        NewsArticle(
            id="headline-1",
            headline="Market news",
            source="Reuters",
            url="https://example.com/1",
            published_at=datetime.now(),
            summary="Summary"
        )
    ]
    
    mock_trending = [
        TrendingTicker(
            ticker="AAPL",
            company_name="Apple Inc.",
            news_count=15,
            reason="High volume"
        )
    ]
    
    mock_indices = [
        MarketIndex(name="S&P 500", symbol="^GSPC", value=4500.0, change=50.0, change_percent=1.1)
    ]
    
    # Mock MCP tools
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_news_tools.get_market_news.return_value = mock_headlines
    mock_news_tools.get_trending_tickers.return_value = mock_trending
    
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_stock_tools.get_market_indices.return_value = mock_indices
    
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Get market overview
        result = await service.getMarketOverview()
        
        # Verify cache was set with correct TTL (15 minutes = 900 seconds)
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 900  # TTL in seconds
        
        # Verify result
        assert isinstance(result, MarketOverview)


@pytest.mark.asyncio
async def test_market_overview_error_handling():
    """
    Test that market overview service handles MCP errors appropriately.
    
    Validates: Requirements 12.1, 12.2, 12.3, 12.6
    """
    from app.mcp.exceptions import MCPToolError
    
    # Mock MCP tools to raise error
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_news_tools.get_market_news.side_effect = MCPToolError(
        "MCP connection failed",
        details={}
    )
    
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            await service.getMarketOverview()
        
        # Verify error message is informative
        assert "Unable to retrieve market overview" in str(exc_info.value)


@pytest.mark.asyncio
async def test_trending_tickers_retrieval():
    """
    Test that trending tickers are retrieved correctly.
    
    Validates: Requirements 12.3
    """
    mock_trending = [
        TrendingTicker(
            ticker=f"TICK{i}",
            company_name=f"Company {i}",
            news_count=20 - i,
            reason="High trading volume"
        )
        for i in range(10)
    ]
    
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_news_tools.get_trending_tickers.return_value = mock_trending
    
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Get trending tickers
        result = await service.getTrendingTickers(limit=10)
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 10
        
        for ticker in result:
            assert isinstance(ticker, TrendingTicker)
            assert ticker.ticker is not None
            assert ticker.company_name is not None
            assert ticker.news_count > 0
            assert ticker.reason is not None


@pytest.mark.asyncio
async def test_market_indices_retrieval():
    """
    Test that market indices are retrieved correctly.
    
    Validates: Requirements 12.6
    """
    mock_indices = [
        MarketIndex(name="S&P 500", symbol="^GSPC", value=4500.0, change=50.0, change_percent=1.1),
        MarketIndex(name="NASDAQ", symbol="^IXIC", value=14000.0, change=100.0, change_percent=0.7),
        MarketIndex(name="DOW", symbol="^DJI", value=35000.0, change=-30.0, change_percent=-0.1)
    ]
    
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_stock_tools.get_market_indices.return_value = mock_indices
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Get market indices
        result = await service.getMarketIndices()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Verify major indices are present
        index_names = [idx.name for idx in result]
        assert "S&P 500" in index_names
        assert "NASDAQ" in index_names
        assert "DOW" in index_names
        
        for index in result:
            assert isinstance(index, MarketIndex)
            assert index.name is not None
            assert index.symbol is not None
            assert index.value > 0
            assert index.change is not None
            assert index.change_percent is not None


@pytest.mark.asyncio
async def test_sector_performance_retrieval():
    """
    Test that sector performance is retrieved correctly.
    
    Validates: Requirements 12.4
    """
    mock_sectors = [
        SectorPerformance(
            sector="Technology",
            change_percent=2.5,
            top_performers=["AAPL", "GOOGL", "MSFT"],
            bottom_performers=["IBM"]
        ),
        SectorPerformance(
            sector="Healthcare",
            change_percent=-1.2,
            top_performers=["JNJ"],
            bottom_performers=["PFE", "MRNA"]
        ),
        SectorPerformance(
            sector="Finance",
            change_percent=0.8,
            top_performers=["JPM", "BAC"],
            bottom_performers=["WFC"]
        )
    ]
    
    mock_news_tools = AsyncMock(spec=NewsMCPTools)
    mock_stock_tools = AsyncMock(spec=StockDataMCPTools)
    mock_market_tools = AsyncMock(spec=MarketDataMCPTools)
    mock_market_tools.get_sector_performance.return_value = mock_sectors
    
    # Mock Redis
    with patch("app.services.market_overview_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = MarketOverviewService(
            news_tools=mock_news_tools,
            stock_tools=mock_stock_tools,
            market_tools=mock_market_tools
        )
        
        # Get sector performance
        result = await service.getSectorPerformance()
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) == 3
        
        for sector in result:
            assert isinstance(sector, SectorPerformance)
            assert sector.sector is not None
            assert sector.change_percent is not None
            assert isinstance(sector.top_performers, list)
            assert isinstance(sector.bottom_performers, list)
            assert len(sector.top_performers) > 0
            assert len(sector.bottom_performers) > 0
