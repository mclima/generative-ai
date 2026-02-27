"""
Property-based tests for Stock Data Service.

Feature: us-stock-assistant
Property 12: Historical Data Retrieval
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch
from datetime import date, timedelta
from decimal import Decimal

from app.services.stock_data_service import StockDataService
from app.mcp.tools.stock_data import (
    StockDataMCPTools,
    StockPrice,
    HistoricalDataPoint,
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
def date_range_strategy(draw):
    """Generate valid date ranges."""
    # Generate dates within a reasonable range
    start_date = draw(st.dates(
        min_value=date(2020, 1, 1),
        max_value=date(2024, 12, 31)
    ))
    
    # End date is after start date
    days_diff = draw(st.integers(min_value=1, max_value=365))
    end_date = start_date + timedelta(days=days_diff)
    
    # Ensure end date doesn't exceed max
    if end_date > date(2024, 12, 31):
        end_date = date(2024, 12, 31)
    
    return start_date, end_date


@st.composite
def historical_data_strategy(draw, start_date, end_date):
    """Generate historical data points for a date range."""
    data_points = []
    current_date = start_date
    
    while current_date <= end_date:
        # Generate realistic price data
        open_price = draw(st.floats(min_value=1.0, max_value=1000.0))
        high_price = draw(st.floats(min_value=open_price, max_value=open_price * 1.1))
        low_price = draw(st.floats(min_value=open_price * 0.9, max_value=open_price))
        close_price = draw(st.floats(min_value=low_price, max_value=high_price))
        volume = draw(st.integers(min_value=1000, max_value=1000000000))
        
        data_points.append(HistoricalDataPoint(
            date=current_date,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        ))
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return data_points


# Property 12: Historical Data Retrieval
@pytest.mark.asyncio
@given(
    ticker=ticker_strategy(),
    date_range=date_range_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_historical_data_retrieval_chronological_order(ticker, date_range):
    """
    Property 12: Historical Data Retrieval
    
    For any valid ticker and date range, requesting historical data via MCP
    should return a chronologically ordered list of price data points covering
    the requested period.
    
    Validates: Requirements 3.5
    """
    start_date, end_date = date_range
    
    # Generate mock historical data
    mock_data = []
    current_date = start_date
    while current_date <= end_date:
        mock_data.append(HistoricalDataPoint(
            date=current_date,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000000
        ))
        current_date += timedelta(days=1)
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.get_historical_data.return_value = mock_data
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Get historical data
        result = await service.getHistoricalData(ticker, start_date, end_date)
        
        # Verify MCP was called with correct parameters
        mock_mcp_tools.get_historical_data.assert_called_once_with(
            ticker.upper(), start_date, end_date
        )
        
        # Verify result is a list
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Verify all items are HistoricalDataPoint
        assert all(isinstance(point, HistoricalDataPoint) for point in result)
        
        # Verify chronological order
        dates = [point.date for point in result]
        assert dates == sorted(dates), "Historical data must be in chronological order"
        
        # Verify date range coverage
        assert dates[0] >= start_date, "First date should be >= start_date"
        assert dates[-1] <= end_date, "Last date should be <= end_date"
        
        # Verify data integrity
        for point in result:
            # Prices should be non-negative
            assert point.open >= 0
            assert point.high >= 0
            assert point.low >= 0
            assert point.close >= 0
            
            # High should be >= low
            assert point.high >= point.low
            
            # Open and close should be between low and high
            assert point.low <= point.open <= point.high
            assert point.low <= point.close <= point.high
            
            # Volume should be non-negative
            assert point.volume >= 0


@pytest.mark.asyncio
@given(
    ticker=ticker_strategy(),
    date_range=date_range_strategy()
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_historical_data_caching(ticker, date_range):
    """
    Test that historical data is properly cached with 1-hour TTL.
    
    Validates: Requirements 3.5, 21.5
    """
    start_date, end_date = date_range
    
    # Generate mock historical data
    mock_data = [
        HistoricalDataPoint(
            date=start_date,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000000
        )
    ]
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.get_historical_data.return_value = mock_data
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss on first call
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # First call - should fetch from MCP and cache
        result1 = await service.getHistoricalData(ticker, start_date, end_date)
        
        # Verify MCP was called
        assert mock_mcp_tools.get_historical_data.call_count == 1
        
        # Verify cache was set with correct TTL (1 hour = 3600 seconds)
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 3600  # TTL in seconds
        
        # Verify result
        assert len(result1) > 0


@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_historical_data_error_handling(ticker):
    """
    Test that historical data service handles MCP errors appropriately.
    
    Validates: Requirements 3.4
    """
    from app.mcp.exceptions import MCPToolError
    
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Mock MCP tools to raise MCP error
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.get_historical_data.side_effect = MCPToolError(
        "MCP connection failed",
        details={"ticker": ticker}
    )
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # No cached data
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Should raise ValueError with clear message
        with pytest.raises(ValueError) as exc_info:
            await service.getHistoricalData(ticker, start_date, end_date)
        
        # Verify error message is informative
        assert ticker.upper() in str(exc_info.value)
        assert "Unable to retrieve historical data" in str(exc_info.value)


@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_historical_data_empty_range(ticker):
    """
    Test that historical data handles empty date ranges appropriately.
    
    Validates: Requirements 3.5
    """
    # Same start and end date
    start_date = date(2024, 1, 15)
    end_date = date(2024, 1, 15)
    
    # Mock MCP tools to return single data point
    mock_data = [
        HistoricalDataPoint(
            date=start_date,
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=1000000
        )
    ]
    
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.get_historical_data.return_value = mock_data
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Get historical data
        result = await service.getHistoricalData(ticker, start_date, end_date)
        
        # Should return at least one data point
        assert len(result) >= 1
        assert result[0].date == start_date
