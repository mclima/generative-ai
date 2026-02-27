"""
Property-based tests for AI Analysis Service.

Feature: us-stock-assistant
Property 17: AI Analysis Completeness
Property 18: AI Analysis Context
Property 19: AI Analysis Error Handling
"""

import pytest
import asyncio
import json
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, date, timedelta
from typing import List

from app.services.ai_analysis_service import (
    AIAnalysisService,
    AnalysisContext,
    HistoricalDataPoint,
    NewsArticle,
    FinancialMetrics,
    MarketConditions,
    StockAnalysis,
    PortfolioAnalysis,
    PriceAnalysis,
    SentimentAnalysis
)


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
def historical_data_strategy(draw):
    """Generate historical data points."""
    num_points = draw(st.integers(min_value=1, max_value=30))
    data_points = []
    
    base_date = datetime.now() - timedelta(days=num_points)
    
    for i in range(num_points):
        open_price = draw(st.floats(min_value=1.0, max_value=1000.0))
        high_price = draw(st.floats(min_value=open_price, max_value=open_price * 1.1))
        low_price = draw(st.floats(min_value=open_price * 0.9, max_value=open_price))
        close_price = draw(st.floats(min_value=low_price, max_value=high_price))
        volume = draw(st.integers(min_value=1000, max_value=1000000000))
        
        data_points.append(HistoricalDataPoint(
            date=base_date + timedelta(days=i),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        ))
    
    return data_points


@st.composite
def news_article_strategy(draw):
    """Generate news articles."""
    num_articles = draw(st.integers(min_value=0, max_value=10))
    articles = []
    
    for i in range(num_articles):
        sentiment_label = draw(st.sampled_from(["positive", "negative", "neutral"]))
        sentiment_score = draw(st.floats(min_value=-1.0, max_value=1.0))
        
        articles.append(NewsArticle(
            headline=draw(st.text(min_size=10, max_size=100)),
            source=draw(st.sampled_from(["Reuters", "Bloomberg", "CNBC", "WSJ"])),
            published_at=datetime.now() - timedelta(days=draw(st.integers(min_value=0, max_value=7))),
            summary=draw(st.text(min_size=20, max_size=200)),
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score
        ))
    
    return articles


@st.composite
def financial_metrics_strategy(draw, ticker):
    """Generate financial metrics."""
    return FinancialMetrics(
        ticker=ticker,
        pe_ratio=draw(st.floats(min_value=1.0, max_value=100.0)),
        eps=draw(st.floats(min_value=0.1, max_value=50.0)),
        dividend_yield=draw(st.floats(min_value=0.0, max_value=10.0)),
        beta=draw(st.floats(min_value=0.1, max_value=3.0)),
        fifty_two_week_high=draw(st.floats(min_value=50.0, max_value=500.0)),
        fifty_two_week_low=draw(st.floats(min_value=10.0, max_value=100.0))
    )


@st.composite
def market_conditions_strategy(draw):
    """Generate market conditions."""
    return MarketConditions(
        market_sentiment=draw(st.sampled_from(["positive", "negative", "neutral"])),
        sp500_change=draw(st.floats(min_value=-5.0, max_value=5.0)),
        nasdaq_change=draw(st.floats(min_value=-5.0, max_value=5.0)),
        dow_change=draw(st.floats(min_value=-5.0, max_value=5.0))
    )


@st.composite
def analysis_context_strategy(draw, ticker):
    """Generate complete analysis context."""
    return AnalysisContext(
        historical_data=draw(historical_data_strategy()),
        news=draw(news_article_strategy()),
        financial_metrics=draw(financial_metrics_strategy(ticker)),
        market_conditions=draw(market_conditions_strategy())
    )


def create_mock_llm_response(ticker: str):
    """Create a mock LLM response for stock analysis."""
    mock_response = Mock()
    # Use json.dumps to avoid f-string issues with nested braces
    import json
    data = {
        "ticker": ticker,
        "summary": f"This is a comprehensive analysis of {ticker} stock based on recent data.",
        "price_analysis": {
            "trend": "bullish",
            "support": 95.50,
            "resistance": 110.25,
            "volatility": "medium"
        },
        "sentiment_analysis": {
            "overall": "positive",
            "score": 0.65,
            "news_count": 5
        },
        "recommendations": [
            "Consider buying on dips near support level",
            "Monitor earnings report next quarter",
            "Set stop-loss at $90"
        ],
        "risks": [
            "Market volatility may increase",
            "Sector-specific headwinds",
            "Regulatory concerns"
        ],
        "generated_at": datetime.now().isoformat()
    }
    mock_response.content = json.dumps(data)
    return mock_response


def create_mock_portfolio_llm_response():
    """Create a mock LLM response for portfolio analysis."""
    mock_response = Mock()
    # Use json.dumps to avoid f-string issues with nested braces
    import json
    data = {
        "overall_health": "good",
        "diversification_score": 75.5,
        "risk_level": "medium",
        "rebalancing_suggestions": [
            {
                "action": "buy",
                "ticker": "AAPL",
                "reason": "Underweight in technology sector",
                "suggested_amount": 1000.0
            },
            {
                "action": "sell",
                "ticker": "XYZ",
                "reason": "Overweight position with declining fundamentals",
                "suggested_amount": 500.0
            }
        ],
        "underperforming_stocks": ["XYZ", "ABC"],
        "opportunities": [
            "Consider adding exposure to healthcare sector",
            "Increase allocation to dividend-paying stocks"
        ]
    }
    mock_response.content = json.dumps(data)
    return mock_response


# Property 17: AI Analysis Completeness
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy(),
    context=st.builds(
        lambda t: analysis_context_strategy(t),
        t=ticker_strategy()
    ).flatmap(lambda f: f)
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.data_too_large]
)
async def test_ai_analysis_completeness(ticker, context):
    """
    Property 17: AI Analysis Completeness
    
    For any stock analysis request, the AI analysis service should return
    a structured analysis containing all required sections (price analysis,
    sentiment analysis, recommendations, risks).
    
    Validates: Requirements 4.1, 4.5
    """
    # Mock LangChain LLM
    with patch("app.services.ai_analysis_service.ChatOpenAI") as mock_openai:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = create_mock_llm_response(ticker)
        mock_openai.return_value = mock_llm
        
        # Create service with mock API key
        service = AIAnalysisService(api_key="test-api-key")
        
        # Perform analysis
        result = await service.analyzeStock(ticker, context)
        
        # Verify result is StockAnalysis
        assert isinstance(result, StockAnalysis)
        
        # Verify all required sections are present
        assert result.ticker == ticker.upper()
        assert result.summary is not None
        assert len(result.summary) > 0
        
        # Verify price analysis section
        assert isinstance(result.price_analysis, PriceAnalysis)
        assert result.price_analysis.trend in ["bullish", "bearish", "neutral"]
        assert result.price_analysis.volatility in ["high", "medium", "low"]
        # Support and resistance are optional but should be present in most cases
        
        # Verify sentiment analysis section
        assert isinstance(result.sentiment_analysis, SentimentAnalysis)
        assert result.sentiment_analysis.overall in ["positive", "negative", "neutral"]
        assert -1.0 <= result.sentiment_analysis.score <= 1.0
        assert result.sentiment_analysis.news_count >= 0
        
        # Verify recommendations section
        assert isinstance(result.recommendations, list)
        assert len(result.recommendations) > 0
        assert all(isinstance(rec, str) for rec in result.recommendations)
        
        # Verify risks section
        assert isinstance(result.risks, list)
        assert len(result.risks) > 0
        assert all(isinstance(risk, str) for risk in result.risks)
        
        # Verify generated_at timestamp
        assert isinstance(result.generated_at, datetime)
        assert result.generated_at <= datetime.now()


# Property 18: AI Analysis Context
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy(),
    context=st.builds(
        lambda t: analysis_context_strategy(t),
        t=ticker_strategy()
    ).flatmap(lambda f: f)
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.data_too_large]
)
async def test_ai_analysis_context_inclusion(ticker, context):
    """
    Property 18: AI Analysis Context
    
    For any stock analysis, the analysis context should include recent news,
    financial metrics, and market data retrieved via MCP before generating insights.
    
    Validates: Requirements 4.2
    """
    # Mock LangChain LLM
    with patch("app.services.ai_analysis_service.ChatOpenAI") as mock_openai:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = create_mock_llm_response(ticker)
        mock_openai.return_value = mock_llm
        
        # Create service with mock API key
        service = AIAnalysisService(api_key="test-api-key")
        
        # Perform analysis
        result = await service.analyzeStock(ticker, context)
        
        # Verify LLM was called
        assert mock_llm.ainvoke.call_count == 1
        
        # Get the prompt that was sent to the LLM
        call_args = mock_llm.ainvoke.call_args
        prompt_messages = call_args[0][0]
        
        # Convert messages to string for inspection
        prompt_text = str(prompt_messages)
        
        # Verify context data was included in the prompt
        # Check that ticker is mentioned
        assert ticker.upper() in prompt_text or ticker in prompt_text
        
        # If historical data is present, verify it's included
        if context.historical_data:
            # Should mention historical data or price data
            assert any(keyword in prompt_text.lower() for keyword in [
                "historical", "price", "open", "close", "volume"
            ])
        
        # If news is present, verify it's included
        if context.news:
            # Should mention news or articles
            assert any(keyword in prompt_text.lower() for keyword in [
                "news", "article", "headline"
            ])
        
        # If financial metrics are present, verify they're included
        if context.financial_metrics:
            # Should mention financial metrics
            assert any(keyword in prompt_text.lower() for keyword in [
                "financial", "metrics", "p/e", "eps", "beta"
            ])
        
        # If market conditions are present, verify they're included
        if context.market_conditions:
            # Should mention market conditions
            assert any(keyword in prompt_text.lower() for keyword in [
                "market", "s&p", "nasdaq", "dow", "sentiment"
            ])


# Property 19: AI Analysis Error Handling
@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_ai_analysis_no_api_key_error(ticker):
    """
    Property 19: AI Analysis Error Handling (No API Key)
    
    For any analysis request when API key is not configured, the AI service
    should return an error response with a clear explanation rather than
    incomplete or unreliable analysis.
    
    Validates: Requirements 4.4
    """
    # Create service without API key
    with patch("app.services.ai_analysis_service.get_settings") as mock_settings:
        mock_config = Mock()
        mock_config.openai_api_key = ""
        mock_settings.return_value = mock_config
        
        service = AIAnalysisService()
        
        # Create minimal context
        context = AnalysisContext()
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            await service.analyzeStock(ticker, context)
        
        # Verify error message is informative
        error_message = str(exc_info.value)
        assert "not available" in error_message.lower() or "not configured" in error_message.lower()
        assert "api key" in error_message.lower()


@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,  # Reduced since each test takes 11+ seconds
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_ai_analysis_timeout_error(ticker):
    """
    Property 19: AI Analysis Error Handling (Timeout)
    
    For any analysis request that exceeds the timeout limit, the AI service
    should return a timeout error with a clear explanation.
    
    Validates: Requirements 4.3, 4.4
    """
    # Mock LangChain LLM to simulate timeout
    with patch("app.services.ai_analysis_service.ChatOpenAI") as mock_openai:
        mock_llm = AsyncMock()
        
        # Simulate timeout by making ainvoke take too long
        async def slow_invoke(*args, **kwargs):
            await asyncio.sleep(11)  # Slightly longer than 10-second timeout
            return create_mock_llm_response(ticker)
        
        mock_llm.ainvoke = slow_invoke
        mock_openai.return_value = mock_llm
        
        # Create service with mock API key
        service = AIAnalysisService(api_key="test-api-key")
        
        # Create minimal context
        context = AnalysisContext()
        
        # Should raise TimeoutError
        with pytest.raises(TimeoutError) as exc_info:
            await service.analyzeStock(ticker, context)
        
        # Verify error message mentions timeout
        error_message = str(exc_info.value)
        assert "timeout" in error_message.lower() or "time limit" in error_message.lower()
        assert "10" in error_message or "second" in error_message


@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_ai_analysis_parse_error(ticker):
    """
    Property 19: AI Analysis Error Handling (Parse Error)
    
    For any analysis request where the LLM response cannot be parsed,
    the AI service should return an error with a clear explanation.
    
    Validates: Requirements 4.4
    """
    # Mock LangChain LLM to return invalid JSON
    with patch("app.services.ai_analysis_service.ChatOpenAI") as mock_openai:
        mock_llm = AsyncMock()
        
        # Return invalid response
        mock_response = Mock()
        mock_response.content = "This is not valid JSON"
        mock_llm.ainvoke.return_value = mock_response
        
        mock_openai.return_value = mock_llm
        
        # Create service with mock API key
        service = AIAnalysisService(api_key="test-api-key")
        
        # Create minimal context
        context = AnalysisContext()
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            await service.analyzeStock(ticker, context)
        
        # Verify error message is informative
        error_message = str(exc_info.value)
        assert "unable to generate" in error_message.lower() or "could not be parsed" in error_message.lower()
        assert ticker.upper() in error_message


# Portfolio Analysis Tests
@pytest.mark.asyncio
@given(
    num_positions=st.integers(min_value=1, max_value=10)
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_portfolio_analysis_completeness(num_positions):
    """
    Test that portfolio analysis returns all required sections.
    
    Validates: Requirements 4.1
    """
    # Generate mock portfolio positions
    positions = []
    for i in range(num_positions):
        positions.append({
            "ticker": f"TICK{i}",
            "quantity": 100,
            "current_value": 10000.0,
            "gain_loss": 500.0,
            "gain_loss_percent": 5.0
        })
    
    # Generate mock portfolio metrics
    metrics = {
        "total_value": 100000.0,
        "total_gain_loss": 5000.0,
        "total_gain_loss_percent": 5.0,
        "daily_gain_loss": 200.0,
        "diversity_score": 75.0,
        "performance_by_period": {
            "1D": 0.5,
            "1W": 2.0,
            "1M": 5.0
        }
    }
    
    # Mock LangChain LLM
    with patch("app.services.ai_analysis_service.ChatOpenAI") as mock_openai:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = create_mock_portfolio_llm_response()
        mock_openai.return_value = mock_llm
        
        # Create service with mock API key
        service = AIAnalysisService(api_key="test-api-key")
        
        # Perform analysis
        result = await service.analyzePortfolio(positions, metrics)
        
        # Verify result is PortfolioAnalysis
        assert isinstance(result, PortfolioAnalysis)
        
        # Verify all required sections are present
        assert result.overall_health in ["good", "fair", "poor"]
        assert 0.0 <= result.diversification_score <= 100.0
        assert result.risk_level in ["high", "medium", "low"]
        
        # Verify rebalancing suggestions
        assert isinstance(result.rebalancing_suggestions, list)
        for suggestion in result.rebalancing_suggestions:
            assert suggestion.action in ["buy", "sell", "hold"]
            assert len(suggestion.ticker) > 0
            assert len(suggestion.reason) > 0
        
        # Verify underperforming stocks list
        assert isinstance(result.underperforming_stocks, list)
        
        # Verify opportunities list
        assert isinstance(result.opportunities, list)


@pytest.mark.asyncio
async def test_portfolio_analysis_no_api_key_error():
    """
    Test that portfolio analysis handles missing API key appropriately.
    
    Validates: Requirements 4.4
    """
    # Create service without API key
    with patch("app.services.ai_analysis_service.get_settings") as mock_settings:
        mock_config = Mock()
        mock_config.openai_api_key = ""
        mock_settings.return_value = mock_config
        
        service = AIAnalysisService()
        
        # Create minimal portfolio data
        positions = [{"ticker": "AAPL", "quantity": 100, "current_value": 10000.0, "gain_loss": 500.0, "gain_loss_percent": 5.0}]
        metrics = {"total_value": 10000.0}
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            await service.analyzePortfolio(positions, metrics)
        
        # Verify error message is informative
        error_message = str(exc_info.value)
        assert "not available" in error_message.lower() or "not configured" in error_message.lower()
        assert "api key" in error_message.lower()


@pytest.mark.asyncio
async def test_analysis_timeout_within_limit():
    """
    Test that analysis completes within the 10-second timeout limit.
    
    Validates: Requirements 4.3
    """
    ticker = "AAPL"
    
    # Mock LangChain LLM with fast response
    with patch("app.services.ai_analysis_service.ChatOpenAI") as mock_openai:
        mock_llm = AsyncMock()
        
        # Simulate fast response (under timeout)
        async def fast_invoke(*args, **kwargs):
            await asyncio.sleep(0.1)  # 100ms
            return create_mock_llm_response(ticker)
        
        mock_llm.ainvoke = fast_invoke
        mock_openai.return_value = mock_llm
        
        # Create service with mock API key
        service = AIAnalysisService(api_key="test-api-key")
        
        # Create minimal context
        context = AnalysisContext()
        
        # Measure execution time
        start_time = asyncio.get_event_loop().time()
        result = await service.analyzeStock(ticker, context)
        end_time = asyncio.get_event_loop().time()
        
        # Verify analysis completed
        assert isinstance(result, StockAnalysis)
        
        # Verify it completed well within timeout
        execution_time = end_time - start_time
        assert execution_time < 10.0  # Should be under 10 seconds
