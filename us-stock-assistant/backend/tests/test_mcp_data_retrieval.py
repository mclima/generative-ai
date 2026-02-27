"""
Property-based tests for MCP data retrieval.

Feature: us-stock-assistant
Property 10: MCP Data Retrieval Completeness
Property 11: MCP Error Handling with Fallback
Property 14: MCP Tool Availability
Property 16: MCP Provider Interchangeability
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch
from datetime import date, datetime
import httpx

from app.mcp.client import MCPClient, MCPResponse
from app.mcp.config import MCPConfig
from app.mcp.tools.stock_data import (
    StockDataMCPTools,
    StockPrice,
    HistoricalDataPoint,
    CompanyInfo,
    FinancialMetrics,
    StockSearchResult,
    MarketIndex,
)
from app.mcp.exceptions import MCPToolError, MCPValidationError


# Hypothesis strategies
@st.composite
def ticker_strategy(draw):
    """Generate valid ticker symbols."""
    return draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=("Lu",))))


@st.composite
def stock_price_data_strategy(draw):
    """Generate valid stock price data."""
    ticker = draw(ticker_strategy())
    return {
        "ticker": ticker,
        "price": draw(st.floats(min_value=0.01, max_value=10000)),
        "change": draw(st.floats(min_value=-1000, max_value=1000)),
        "change_percent": draw(st.floats(min_value=-100, max_value=100)),
        "volume": draw(st.integers(min_value=0, max_value=1000000000)),
        "timestamp": datetime.now().isoformat()
    }


# Property 10: MCP Data Retrieval Completeness
@pytest.mark.asyncio
@given(ticker=ticker_strategy(), price_data=stock_price_data_strategy())
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_mcp_data_retrieval_completeness(ticker, price_data):
    """
    Property 10: MCP Data Retrieval Completeness
    
    For any stock ticker in a user's portfolio, requesting current price data
    via MCP should return all required fields (price, change, changePercent,
    volume, timestamp).
    
    Validates: Requirements 3.1, 3.2
    """
    config = MCPConfig(
        server_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Mock stock price response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": price_data
        }
        mock_client.post.return_value = mock_response
        
        # Create client and tools
        client = MCPClient(config)
        await client.connect()
        tools = StockDataMCPTools(client)
        
        try:
            # Get stock price
            result = await tools.get_stock_price(ticker)
            
            # Verify all required fields are present
            assert result.ticker is not None
            assert result.price is not None
            assert result.change is not None
            assert result.change_percent is not None
            assert result.volume is not None
            assert result.timestamp is not None
            
            # Verify data types
            assert isinstance(result.ticker, str)
            assert isinstance(result.price, float)
            assert isinstance(result.change, float)
            assert isinstance(result.change_percent, float)
            assert isinstance(result.volume, int)
            assert isinstance(result.timestamp, datetime)
            
        finally:
            await client.disconnect()


# Property 11: MCP Error Handling with Fallback
@pytest.mark.asyncio
@given(ticker=ticker_strategy())
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_mcp_error_handling(ticker):
    """
    Property 11: MCP Error Handling with Fallback
    
    For any MCP request that returns invalid or error data, the stock data
    service should log the error and raise an appropriate exception.
    
    Validates: Requirements 3.4
    """
    config = MCPConfig(
        server_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": "Stock not found"
        }
        mock_client.post.return_value = mock_response
        
        # Create client and tools
        client = MCPClient(config)
        await client.connect()
        tools = StockDataMCPTools(client)
        
        try:
            # Should raise MCPToolError
            with pytest.raises(MCPToolError) as exc_info:
                await tools.get_stock_price(ticker)
            
            # Verify error details
            assert "failed" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
            assert ticker.upper() in exc_info.value.details.get("ticker", "")
            
        finally:
            await client.disconnect()


# Property 14: MCP Tool Availability
@pytest.mark.asyncio
async def test_mcp_tool_availability():
    """
    Property 14: MCP Tool Availability
    
    For any required financial data operation (stock prices, historical data,
    company info, financial metrics), the MCP server should expose a
    corresponding tool that can be invoked by the client.
    
    Validates: Requirements 10.1
    """
    config = MCPConfig(
        server_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    required_tools = [
        "get_stock_price",
        "get_historical_data",
        "get_company_info",
        "get_financial_metrics",
        "search_stocks",
        "get_market_indices"
    ]
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        
        # Mock tools list
        mock_tools_response = Mock()
        mock_tools_response.status_code = 200
        mock_tools_response.json.return_value = {
            "tools": [
                {"name": tool, "description": f"Tool for {tool}", "parameters": {}}
                for tool in required_tools
            ]
        }
        
        def get_side_effect(endpoint):
            if endpoint == "/health":
                return mock_health
            elif endpoint == "/tools":
                return mock_tools_response
            return mock_health
        
        mock_client.get.side_effect = get_side_effect
        
        # Create client
        client = MCPClient(config)
        await client.connect()
        
        try:
            # List available tools
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            
            # Verify all required tools are available
            for required_tool in required_tools:
                assert required_tool in tool_names, f"Required tool '{required_tool}' not available"
            
        finally:
            await client.disconnect()


# Property 16: MCP Provider Interchangeability
@pytest.mark.asyncio
@given(ticker=ticker_strategy(), price_data=stock_price_data_strategy())
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_mcp_provider_interchangeability(ticker, price_data):
    """
    Property 16: MCP Provider Interchangeability
    
    For any two different financial data providers configured in the MCP server,
    switching between them should not change the interface or data format
    returned to the client.
    
    Validates: Requirements 10.6
    """
    # Configure two different providers
    provider1_config = MCPConfig(
        server_url="http://provider1:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    provider2_config = MCPConfig(
        server_url="http://provider2:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Mock response (same format for both providers)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": price_data
        }
        mock_client.post.return_value = mock_response
        
        # Test provider 1
        client1 = MCPClient(provider1_config)
        await client1.connect()
        tools1 = StockDataMCPTools(client1)
        
        try:
            result1 = await tools1.get_stock_price(ticker)
            
            # Verify result structure
            assert hasattr(result1, 'ticker')
            assert hasattr(result1, 'price')
            assert hasattr(result1, 'change')
            assert hasattr(result1, 'change_percent')
            assert hasattr(result1, 'volume')
            assert hasattr(result1, 'timestamp')
            
        finally:
            await client1.disconnect()
        
        # Test provider 2
        client2 = MCPClient(provider2_config)
        await client2.connect()
        tools2 = StockDataMCPTools(client2)
        
        try:
            result2 = await tools2.get_stock_price(ticker)
            
            # Verify same interface (same attributes)
            assert hasattr(result2, 'ticker')
            assert hasattr(result2, 'price')
            assert hasattr(result2, 'change')
            assert hasattr(result2, 'change_percent')
            assert hasattr(result2, 'volume')
            assert hasattr(result2, 'timestamp')
            
            # Verify same data types
            assert type(result1.ticker) == type(result2.ticker)
            assert type(result1.price) == type(result2.price)
            assert type(result1.change) == type(result2.change)
            assert type(result1.change_percent) == type(result2.change_percent)
            assert type(result1.volume) == type(result2.volume)
            assert type(result1.timestamp) == type(result2.timestamp)
            
        finally:
            await client2.disconnect()


@pytest.mark.asyncio
async def test_historical_data_chronological_order():
    """
    Test that historical data is returned in chronological order.
    
    Validates: Requirements 3.5
    """
    config = MCPConfig(
        server_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Mock historical data response (unordered)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "date": "2024-01-03",
                    "open": 150.0,
                    "high": 155.0,
                    "low": 149.0,
                    "close": 153.0,
                    "volume": 1000000
                },
                {
                    "date": "2024-01-01",
                    "open": 145.0,
                    "high": 148.0,
                    "low": 144.0,
                    "close": 147.0,
                    "volume": 900000
                },
                {
                    "date": "2024-01-02",
                    "open": 147.0,
                    "high": 151.0,
                    "low": 146.0,
                    "close": 150.0,
                    "volume": 950000
                }
            ]
        }
        mock_client.post.return_value = mock_response
        
        # Create client and tools
        client = MCPClient(config)
        await client.connect()
        tools = StockDataMCPTools(client)
        
        try:
            # Get historical data
            result = await tools.get_historical_data(
                "AAPL",
                date(2024, 1, 1),
                date(2024, 1, 3)
            )
            
            # Verify chronological order
            assert len(result) == 3
            assert result[0].date == date(2024, 1, 1)
            assert result[1].date == date(2024, 1, 2)
            assert result[2].date == date(2024, 1, 3)
            
        finally:
            await client.disconnect()


@pytest.mark.asyncio
async def test_search_results_relevance_ranking():
    """
    Test that search results are ranked by relevance score.
    
    Validates: Requirements 8.2
    """
    config = MCPConfig(
        server_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=10,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Mock search response (unordered)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": [
                {
                    "ticker": "AAPL",
                    "company_name": "Apple Inc.",
                    "exchange": "NASDAQ",
                    "relevance_score": 0.95
                },
                {
                    "ticker": "APLE",
                    "company_name": "Apple Hospitality REIT",
                    "exchange": "NYSE",
                    "relevance_score": 0.65
                },
                {
                    "ticker": "APL",
                    "company_name": "Apollo Corp",
                    "exchange": "NASDAQ",
                    "relevance_score": 0.80
                }
            ]
        }
        mock_client.post.return_value = mock_response
        
        # Create client and tools
        client = MCPClient(config)
        await client.connect()
        tools = StockDataMCPTools(client)
        
        try:
            # Search stocks
            result = await tools.search_stocks("apple")
            
            # Verify relevance ranking (descending)
            assert len(result) == 3
            assert result[0].relevance_score >= result[1].relevance_score
            assert result[1].relevance_score >= result[2].relevance_score
            assert result[0].ticker == "AAPL"
            
        finally:
            await client.disconnect()
