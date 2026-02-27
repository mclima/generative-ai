"""
Property-based tests for Sentiment Analysis.

Feature: us-stock-assistant
Property 36: News Sentiment Assignment
Property 37: News Display Completeness
Property 39: Stock Sentiment Aggregation
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from typing import List

from app.services.sentiment_analyzer import SentimentAnalyzer, SentimentScore, StockSentiment
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
def news_article_strategy(draw, ticker: str = None, sentiment_hint: str = None):
    """Generate a news article with optional sentiment hint."""
    
    # Headlines with different sentiments
    positive_headlines = [
        "Stock reaches new high",
        "Company beats earnings expectations",
        "Strong growth reported",
        "Analyst upgrades rating to buy",
        "Profits surge in latest quarter",
        "Record revenue announced"
    ]
    
    negative_headlines = [
        "Stock falls on weak earnings",
        "Company misses revenue targets",
        "Analyst downgrades to sell",
        "Losses mount in latest quarter",
        "Concerns over declining sales",
        "Lawsuit filed against company"
    ]
    
    neutral_headlines = [
        "Company announces new CEO",
        "Quarterly report released",
        "Board meeting scheduled",
        "New office location opened",
        "Partnership agreement signed"
    ]
    
    # Select headline based on sentiment hint
    if sentiment_hint == "positive":
        headline = draw(st.sampled_from(positive_headlines))
    elif sentiment_hint == "negative":
        headline = draw(st.sampled_from(negative_headlines))
    else:
        headline = draw(st.sampled_from(neutral_headlines))
    
    if ticker:
        headline = f"{ticker} {headline}"
    
    sources = ["Reuters", "Bloomberg", "CNBC", "WSJ", "MarketWatch"]
    
    return NewsArticle(
        id=draw(st.text(min_size=10, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")))),
        headline=headline,
        source=draw(st.sampled_from(sources)),
        url=f"https://example.com/article/{draw(st.integers(min_value=1000, max_value=9999))}",
        published_at=datetime.now() - timedelta(hours=draw(st.integers(min_value=0, max_value=48))),
        summary=draw(st.text(min_size=50, max_size=200))
    )


# Property 36: News Sentiment Assignment
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_sentiment_assignment(ticker):
    """
    Property 36: News Sentiment Assignment
    
    For any news article retrieved by the news service, the sentiment analyzer
    should assign a sentiment score (positive, negative, or neutral) with a
    confidence value.
    
    Validates: Requirements 11.2
    """
    # Create a news article
    article = NewsArticle(
        id="test-article-1",
        headline=f"{ticker} announces strong quarterly earnings",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="Company reports record profits and beats analyst expectations"
    )
    
    # Create sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Analyze sentiment
    sentiment = analyzer.analyzeSentiment(article)
    
    # Verify sentiment score structure
    assert isinstance(sentiment, SentimentScore)
    assert sentiment.label in ["positive", "negative", "neutral"]
    assert isinstance(sentiment.score, float)
    assert isinstance(sentiment.confidence, float)
    
    # Verify score range (-1 to 1)
    assert -1.0 <= sentiment.score <= 1.0
    
    # Verify confidence range (0 to 1)
    assert 0.0 <= sentiment.confidence <= 1.0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_positive_sentiment_detection(ticker):
    """
    Test that positive sentiment is correctly detected.
    
    Validates: Requirements 11.2
    """
    # Create article with positive keywords
    article = NewsArticle(
        id="test-positive",
        headline=f"{ticker} stock surges on strong earnings beat",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="Company reports record profits with strong growth and rising revenue"
    )
    
    analyzer = SentimentAnalyzer()
    sentiment = analyzer.analyzeSentiment(article)
    
    # Should detect positive sentiment
    assert sentiment.label == "positive"
    assert sentiment.score > 0
    assert sentiment.confidence > 0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_negative_sentiment_detection(ticker):
    """
    Test that negative sentiment is correctly detected.
    
    Validates: Requirements 11.2
    """
    # Create article with negative keywords
    article = NewsArticle(
        id="test-negative",
        headline=f"{ticker} stock falls on weak earnings miss",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="Company reports losses with declining revenue and poor performance"
    )
    
    analyzer = SentimentAnalyzer()
    sentiment = analyzer.analyzeSentiment(article)
    
    # Should detect negative sentiment
    assert sentiment.label == "negative"
    assert sentiment.score < 0
    assert sentiment.confidence > 0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_neutral_sentiment_detection(ticker):
    """
    Test that neutral sentiment is correctly detected.
    
    Validates: Requirements 11.2
    """
    # Create article with no sentiment keywords
    article = NewsArticle(
        id="test-neutral",
        headline=f"{ticker} announces new CEO appointment",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="The board of directors has appointed a new chief executive officer"
    )
    
    analyzer = SentimentAnalyzer()
    sentiment = analyzer.analyzeSentiment(article)
    
    # Should detect neutral sentiment
    assert sentiment.label == "neutral"
    assert -0.2 <= sentiment.score <= 0.2  # Close to zero


# Property 37: News Display Completeness
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_news_display_completeness(ticker):
    """
    Property 37: News Display Completeness
    
    For any news article displayed on the dashboard, it should include headline,
    source, timestamp, and sentiment indicator.
    
    Validates: Requirements 11.3, 11.4
    """
    # Create mock articles
    mock_articles = [
        NewsArticle(
            id=f"article-{i}",
            headline=f"{ticker} news headline {i}",
            source="Reuters",
            url=f"https://example.com/{i}",
            published_at=datetime.now() - timedelta(hours=i),
            summary=f"Summary {i}"
        )
        for i in range(5)
    ]
    
    mock_mcp_tools = AsyncMock(spec=NewsMCPTools)
    mock_mcp_tools.get_stock_news.return_value = mock_articles
    
    # Mock Redis
    with patch("app.services.news_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service with sentiment analyzer
        analyzer = SentimentAnalyzer()
        service = NewsService(mock_mcp_tools, sentiment_analyzer=analyzer)
        
        # Get stock news
        articles = await service.getStockNews(ticker)
        
        # Verify all articles have complete data
        for article in articles:
            # Verify required fields
            assert article.headline is not None and article.headline != ""
            assert article.source is not None and article.source != ""
            assert article.published_at is not None
            assert isinstance(article.published_at, datetime)
            
            # Verify sentiment can be calculated
            sentiment = analyzer.analyzeSentiment(article)
            assert sentiment is not None
            assert sentiment.label in ["positive", "negative", "neutral"]


# Property 39: Stock Sentiment Aggregation
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_stock_sentiment_aggregation(ticker):
    """
    Property 39: Stock Sentiment Aggregation
    
    For any stock with multiple news articles, the sentiment analyzer should
    provide an overall sentiment summary based on aggregating individual
    article sentiments.
    
    Validates: Requirements 11.6
    """
    # Create articles with mixed sentiments
    articles = [
        NewsArticle(
            id="positive-1",
            headline=f"{ticker} stock surges on strong earnings",
            source="Reuters",
            url="https://example.com/1",
            published_at=datetime.now(),
            summary="Record profits and growth"
        ),
        NewsArticle(
            id="positive-2",
            headline=f"{ticker} beats expectations with rising revenue",
            source="Bloomberg",
            url="https://example.com/2",
            published_at=datetime.now(),
            summary="Strong performance continues"
        ),
        NewsArticle(
            id="negative-1",
            headline=f"{ticker} faces concerns over declining sales",
            source="CNBC",
            url="https://example.com/3",
            published_at=datetime.now(),
            summary="Weak performance in key markets"
        )
    ]
    
    analyzer = SentimentAnalyzer()
    
    # Get aggregated sentiment
    stock_sentiment = analyzer.getStockSentiment(ticker, articles)
    
    # Verify structure
    assert isinstance(stock_sentiment, StockSentiment)
    assert stock_sentiment.ticker == ticker.upper()
    assert stock_sentiment.article_count == len(articles)
    assert len(stock_sentiment.recent_articles) == len(articles)
    
    # Verify overall sentiment
    assert isinstance(stock_sentiment.overall_sentiment, SentimentScore)
    assert stock_sentiment.overall_sentiment.label in ["positive", "negative", "neutral"]
    assert -1.0 <= stock_sentiment.overall_sentiment.score <= 1.0
    assert 0.0 <= stock_sentiment.overall_sentiment.confidence <= 1.0
    
    # With 2 positive and 1 negative, overall should be positive
    assert stock_sentiment.overall_sentiment.label == "positive"
    assert stock_sentiment.overall_sentiment.score > 0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_stock_sentiment_aggregation_empty(ticker):
    """
    Test that sentiment aggregation handles empty article list.
    
    Validates: Requirements 11.6
    """
    analyzer = SentimentAnalyzer()
    
    # Get sentiment with no articles
    stock_sentiment = analyzer.getStockSentiment(ticker, [])
    
    # Should return neutral sentiment with zero confidence
    assert stock_sentiment.ticker == ticker.upper()
    assert stock_sentiment.article_count == 0
    assert len(stock_sentiment.recent_articles) == 0
    assert stock_sentiment.overall_sentiment.label == "neutral"
    assert stock_sentiment.overall_sentiment.score == 0.0
    assert stock_sentiment.overall_sentiment.confidence == 0.0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_stock_sentiment_via_news_service(ticker):
    """
    Test that news service integrates sentiment analysis correctly.
    
    Validates: Requirements 11.2, 11.6
    """
    # Create mock articles
    mock_articles = [
        NewsArticle(
            id="article-1",
            headline=f"{ticker} reports strong earnings growth",
            source="Reuters",
            url="https://example.com/1",
            published_at=datetime.now(),
            summary="Company beats expectations with record profits"
        ),
        NewsArticle(
            id="article-2",
            headline=f"{ticker} stock rises on positive outlook",
            source="Bloomberg",
            url="https://example.com/2",
            published_at=datetime.now(),
            summary="Analysts upgrade rating citing strong fundamentals"
        )
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
        
        # Get stock sentiment
        stock_sentiment = await service.getStockSentiment(ticker)
        
        # Verify sentiment was calculated
        assert isinstance(stock_sentiment, StockSentiment)
        assert stock_sentiment.ticker == ticker.upper()
        assert stock_sentiment.article_count == len(mock_articles)
        
        # With positive articles, sentiment should be positive
        assert stock_sentiment.overall_sentiment.label == "positive"
        assert stock_sentiment.overall_sentiment.score > 0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_sentiment_confidence_increases_with_keywords(ticker):
    """
    Test that confidence increases with more sentiment keywords.
    
    Validates: Requirements 11.2
    """
    # Article with few keywords
    article_low = NewsArticle(
        id="low-confidence",
        headline=f"{ticker} stock rises slightly",
        source="Reuters",
        url="https://example.com/1",
        published_at=datetime.now(),
        summary="Minor increase observed"
    )
    
    # Article with many keywords
    article_high = NewsArticle(
        id="high-confidence",
        headline=f"{ticker} stock surges with strong gains and record profits",
        source="Reuters",
        url="https://example.com/2",
        published_at=datetime.now(),
        summary="Company beats expectations with rising revenue and growth"
    )
    
    analyzer = SentimentAnalyzer()
    
    sentiment_low = analyzer.analyzeSentiment(article_low)
    sentiment_high = analyzer.analyzeSentiment(article_high)
    
    # High keyword article should have higher confidence
    assert sentiment_high.confidence >= sentiment_low.confidence
