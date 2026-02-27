"""
Property-based tests for News Service.

Feature: us-stock-assistant
Property 35: News Retrieval for Portfolio
Property 38: News Deduplication
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from typing import List

from app.services.news_service import NewsService
from app.mcp.tools.news import NewsMCPTools, NewsArticle


# Hypothesis strategies for generating test data
@st.composite
def ticker_strategy(draw):
    """Generate valid stock ticker symbols."""
    return draw(st.text(
        min_size=1,
        max_size=5,
        alphabet=st.characters(whitelist_categories=("Lu",))
    ))


@st.composite
def ticker_list_strategy(draw):
    """Generate a list of stock ticker symbols."""
    num_tickers = draw(st.integers(min_value=1, max_value=10))
    return [draw(ticker_strategy()) for _ in range(num_tickers)]


@st.composite
def news_article_strategy(draw, ticker: str = None):
    """Generate a news article."""
    headlines = [
        "Stock reaches new high",
        "Company announces earnings",
        "Market volatility increases",
        "Analyst upgrades rating",
        "New product launch announced",
        "Quarterly results exceed expectations",
        "CEO steps down",
        "Merger talks underway"
    ]
    
    sources = ["Reuters", "Bloomberg", "CNBC", "WSJ", "MarketWatch", "Financial Times"]
    
    headline = draw(st.sampled_from(headlines))
    if ticker:
        headline = f"{ticker} {headline}"
    
    return NewsArticle(
        id=draw(st.text(min_size=10, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")))),
        headline=headline,
        source=draw(st.sampled_from(sources)),
        url=f"https://example.com/article/{draw(st.integers(min_value=1000, max_value=9999))}",
        published_at=datetime.now() - timedelta(hours=draw(st.integers(min_value=0, max_value=48))),
        summary=draw(st.text(min_size=50, max_size=200))
    )


@st.composite
def news_articles_list_strategy(draw, ticker: str = None, min_size: int = 1, max_size: int = 20):
    """Generate a list of news articles."""
    num_articles = draw(st.integers(min_value=min_size, max_value=max_size))
    return [draw(news_article_strategy(ticker=ticker)) for _ in range(num_articles)]


# Property 35: News Retrieval for Portfolio
@pytest.mark.asyncio
@given(
    tickers=ticker_list_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_retrieval_for_portfolio(tickers):
    """
    Property 35: News Retrieval for Portfolio
    
    For any portfolio with stock positions, loading the dashboard should retrieve
    recent news articles for all stocks in the portfolio.
    
    Validates: Requirements 11.1
    """
    # Mock MCP tools to return news for each ticker
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    
    # Create mock news for each ticker
    def create_mock_news(ticker: str, limit: int):
        return [
            NewsArticle(
                id=f"{ticker}-{i}",
                headline=f"{ticker} news headline {i}",
                source="Reuters",
                url=f"https://example.com/{ticker}/{i}",
                published_at=datetime.now() - timedelta(hours=i),
                summary=f"Summary for {ticker} article {i}"
            )
            for i in range(min(limit, 5))
        ]
    
    mock_mcp_tools.get_stock_news.side_effect = lambda ticker, limit: create_mock_news(ticker, limit)
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Get news for all tickers in portfolio
        results = await service.getBatchStockNews(tickers)
        
        # Verify results contain all unique tickers
        unique_tickers = set(t.upper() for t in tickers)
        assert len(results) == len(unique_tickers)
        
        for ticker in unique_tickers:
            ticker_upper = ticker.upper()
            assert ticker_upper in results
            
            # Verify news articles were retrieved
            articles = results[ticker_upper]
            assert isinstance(articles, list)
            
            # Each ticker should have news articles (or empty list if error)
            assert all(isinstance(article, NewsArticle) for article in articles)
            
            # If articles exist, verify they are recent
            if articles:
                for article in articles:
                    assert article.headline is not None
                    assert article.source is not None
                    assert article.url is not None
                    assert article.published_at is not None
                    assert article.summary is not None


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy(),
    limit=st.integers(min_value=1, max_value=20)
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_retrieval_completeness(ticker, limit):
    """
    Test that news retrieval returns complete article data.
    
    Validates: Requirements 11.1, 11.4
    """
    # Mock MCP tools
    mock_articles = [
        NewsArticle(
            id=f"article-{i}",
            headline=f"{ticker} headline {i}",
            source="Reuters",
            url=f"https://example.com/{i}",
            published_at=datetime.now() - timedelta(hours=i),
            summary=f"Summary {i}"
        )
        for i in range(limit)
    ]
    
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_stock_news.return_value = mock_articles
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Get stock news
        result = await service.getStockNews(ticker, limit=limit)
        
        # Verify result is a list
        assert isinstance(result, list)
        assert len(result) <= limit
        
        # Verify all articles have complete data
        for article in result:
            assert isinstance(article, NewsArticle)
            assert article.id is not None and article.id != ""
            assert article.headline is not None and article.headline != ""
            assert article.source is not None and article.source != ""
            assert article.url is not None and article.url != ""
            assert article.published_at is not None
            assert article.summary is not None


# Property 38: News Deduplication
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_deduplication(ticker):
    """
    Property 38: News Deduplication
    
    For any set of news articles from multiple sources, the news service should
    identify and remove duplicate or highly similar articles.
    
    Validates: Requirements 11.5
    """
    # Create mock articles with duplicates
    base_article = NewsArticle(
        id="article-1",
        headline=f"{ticker} announces quarterly earnings",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="Company reports strong earnings"
    )
    
    # Create duplicate with same headline but different source
    duplicate_article = NewsArticle(
        id="article-2",
        headline=f"{ticker} announces quarterly earnings",  # Same headline
        source="Bloomberg",  # Different source
        url="https://example.com/2",
        published_at=datetime.now(),
        summary="Company reports strong earnings"
    )
    
    # Create unique article
    unique_article = NewsArticle(
        id="article-3",
        headline=f"{ticker} stock price rises",
        source="CNBC",
        url="https://example.com/3",
        published_at=datetime.now(),
        summary="Stock reaches new high"
    )
    
    # Mock MCP tools to return articles with duplicates
    mock_articles = [base_article, duplicate_article, unique_article]
    
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_stock_news.return_value = mock_articles
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Get stock news
        result = await service.getStockNews(ticker, limit=10)
        
        # Verify deduplication occurred
        # Should have 2 articles (base and unique), duplicate should be removed
        assert len(result) == 2
        
        # Verify unique headlines
        headlines = [article.headline for article in result]
        assert len(headlines) == len(set(headlines))
        
        # Verify both unique articles are present
        headline_set = set(headlines)
        assert f"{ticker} announces quarterly earnings" in headline_set
        assert f"{ticker} stock price rises" in headline_set


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_deduplication_case_insensitive(ticker):
    """
    Test that news deduplication is case-insensitive.
    
    Validates: Requirements 11.5
    """
    # Create articles with same headline but different cases
    article1 = NewsArticle(
        id="article-1",
        headline=f"{ticker} ANNOUNCES EARNINGS",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="Summary 1"
    )
    
    article2 = NewsArticle(
        id="article-2",
        headline=f"{ticker} announces earnings",  # Same but lowercase
        source="Bloomberg",
        url="https://example.com/2",
        published_at=datetime.now(),
        summary="Summary 2"
    )
    
    article3 = NewsArticle(
        id="article-3",
        headline=f"{ticker} Announces Earnings",  # Same but title case
        source="CNBC",
        url="https://example.com/3",
        published_at=datetime.now(),
        summary="Summary 3"
    )
    
    mock_articles = [article1, article2, article3]
    
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_stock_news.return_value = mock_articles
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Get stock news
        result = await service.getStockNews(ticker, limit=10)
        
        # Should only have 1 article after deduplication
        assert len(result) == 1
        
        # Verify it's one of the original articles
        assert result[0].id in ["article-1", "article-2", "article-3"]


@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_caching(ticker):
    """
    Test that news is properly cached with 15-minute TTL.
    
    Validates: Requirements 11.7
    """
    mock_articles = [
        NewsArticle(
            id="article-1",
            headline=f"{ticker} news",
            source="Reuters",
            url="https://example.com/1",
            published_at=datetime.now(),
            summary="Summary"
        )
    ]
    
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_stock_news.return_value = mock_articles
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Get stock news
        result = await service.getStockNews(ticker)
        
        # Verify MCP was called
        assert mock_mcp_tools.get_stock_news.call_count == 1
        
        # Verify cache was set with correct TTL (15 minutes = 900 seconds)
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 900  # TTL in seconds
        
        # Verify result
        assert len(result) > 0


@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_error_handling(ticker):
    """
    Test that news service handles MCP errors appropriately.
    
    Validates: Requirements 11.1
    """
    from app.mcp.exceptions import MCPToolError
    
    # Mock MCP tools to raise error
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_stock_news.side_effect = MCPToolError(
        "MCP connection failed",
        details={"ticker": ticker}
    )
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            await service.getStockNews(ticker)
        
        # Verify error message is informative
        assert ticker.upper() in str(exc_info.value)
        assert "Unable to retrieve news" in str(exc_info.value)


@pytest.mark.asyncio
async def test_market_news_retrieval():
    """
    Test that market news retrieval works correctly.
    
    Validates: Requirements 11.1
    """
    mock_articles = [
        NewsArticle(
            id=f"market-{i}",
            headline=f"Market headline {i}",
            source="Reuters",
            url=f"https://example.com/market/{i}",
            published_at=datetime.now() - timedelta(hours=i),
            summary=f"Market summary {i}"
        )
        for i in range(10)
    ]
    
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_market_news.return_value = mock_articles
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = NewsService(mock_mcp_tools)
        
        # Get market news
        result = await service.getMarketNews(limit=20)
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) <= 20
        
        # Verify all articles have complete data
        for article in result:
            assert isinstance(article, NewsArticle)
            assert article.headline is not None
            assert article.source is not None
            assert article.url is not None
            assert article.published_at is not None
