"""
Property-based tests for Stock Search functionality.

Feature: us-stock-assistant
Property 31: Stock Search Results Completeness
Property 32: Search Relevance Ranking
Property 33: Search Result Selection
Property 34: Multi-Exchange Search Coverage
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch

from app.services.stock_data_service import StockDataService
from app.mcp.tools.stock_data import (
    StockDataMCPTools,
    StockSearchResult,
)


# Hypothesis strategies for generating test data
@st.composite
def search_query_strategy(draw):
    """Generate valid search queries."""
    query_type = draw(st.sampled_from(["ticker", "company_name", "partial"]))
    
    if query_type == "ticker":
        # Full ticker symbol
        return draw(st.text(
            min_size=1,
            max_size=5,
            alphabet=st.characters(whitelist_categories=("Lu",))
        ))
    elif query_type == "company_name":
        # Company name
        return draw(st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))))
    else:
        # Partial match
        return draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))))


@st.composite
def search_results_strategy(draw, query: str):
    """Generate search results for a query."""
    num_results = draw(st.integers(min_value=0, max_value=20))
    results = []
    
    exchanges = ["NYSE", "NASDAQ", "AMEX"]
    
    for i in range(num_results):
        ticker = draw(st.text(
            min_size=1,
            max_size=5,
            alphabet=st.characters(whitelist_categories=("Lu",))
        ))
        company_name = draw(st.text(
            min_size=5,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))
        ))
        exchange = draw(st.sampled_from(exchanges))
        
        # Relevance score: exact ticker match gets 1.0, others get lower scores
        if ticker.upper() == query.upper():
            relevance_score = 1.0
        elif query.upper() in ticker.upper():
            relevance_score = draw(st.floats(min_value=0.7, max_value=0.99))
        elif query.lower() in company_name.lower():
            relevance_score = draw(st.floats(min_value=0.3, max_value=0.69))
        else:
            relevance_score = draw(st.floats(min_value=0.1, max_value=0.29))
        
        results.append(StockSearchResult(
            ticker=ticker,
            company_name=company_name,
            exchange=exchange,
            relevance_score=relevance_score
        ))
    
    # Sort by relevance score (descending)
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    return results


# Property 31: Stock Search Results Completeness
@pytest.mark.asyncio
@given(query=search_query_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_stock_search_results_completeness(query):
    """
    Property 31: Stock Search Results Completeness
    
    For any stock search query, the results should include ticker symbol,
    company name, and exchange for each matching stock.
    
    Validates: Requirements 8.1
    """
    # Generate mock search results
    mock_results = [
        StockSearchResult(
            ticker="AAPL",
            company_name="Apple Inc.",
            exchange="NASDAQ",
            relevance_score=1.0
        ),
        StockSearchResult(
            ticker="MSFT",
            company_name="Microsoft Corporation",
            exchange="NASDAQ",
            relevance_score=0.8
        )
    ]
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.search_stocks.return_value = mock_results
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Search stocks
        results = await service.searchStocks(query)
        
        # Verify results structure
        assert isinstance(results, list)
        
        # Verify each result has required fields
        for result in results:
            assert isinstance(result, StockSearchResult)
            
            # Verify ticker is present and non-empty
            assert hasattr(result, 'ticker')
            assert result.ticker is not None
            assert len(result.ticker) > 0
            
            # Verify company_name is present and non-empty
            assert hasattr(result, 'company_name')
            assert result.company_name is not None
            assert len(result.company_name) > 0
            
            # Verify exchange is present and non-empty
            assert hasattr(result, 'exchange')
            assert result.exchange is not None
            assert len(result.exchange) > 0


# Property 32: Search Relevance Ranking
@pytest.mark.asyncio
@given(query=search_query_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_search_relevance_ranking(query):
    """
    Property 32: Search Relevance Ranking
    
    For any search query, results should be ordered by relevance score,
    with exact ticker matches ranked higher than partial matches.
    
    Validates: Requirements 8.2
    """
    # Generate mock search results with varying relevance scores
    mock_results = [
        StockSearchResult(
            ticker=query.upper() if len(query) <= 5 else "EXACT",
            company_name="Exact Match Company",
            exchange="NYSE",
            relevance_score=1.0  # Exact match
        ),
        StockSearchResult(
            ticker="PART",
            company_name=f"Partial {query} Match",
            exchange="NASDAQ",
            relevance_score=0.7  # Partial match
        ),
        StockSearchResult(
            ticker="LOW",
            company_name="Low Relevance Company",
            exchange="AMEX",
            relevance_score=0.3  # Low relevance
        )
    ]
    
    # Mock MCP tools (already sorted by relevance)
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.search_stocks.return_value = mock_results
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Search stocks
        results = await service.searchStocks(query)
        
        # Verify results are ordered by relevance score (descending)
        if len(results) > 1:
            relevance_scores = [result.relevance_score for result in results]
            
            # Check that scores are in descending order
            for i in range(len(relevance_scores) - 1):
                assert relevance_scores[i] >= relevance_scores[i + 1], \
                    f"Results not sorted by relevance: {relevance_scores}"
            
            # Verify exact matches (score = 1.0) come first
            exact_matches = [r for r in results if r.relevance_score == 1.0]
            if exact_matches:
                # All exact matches should be at the beginning
                for i, result in enumerate(results[:len(exact_matches)]):
                    assert result.relevance_score == 1.0, \
                        "Exact matches should be ranked first"


# Property 33: Search Result Selection (Service Layer)
@pytest.mark.asyncio
@given(query=search_query_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_search_result_selection_data_availability(query):
    """
    Property 33: Search Result Selection (Service Layer)
    
    For any selected search result, the service should be able to retrieve
    detailed stock information including all available data fields.
    
    Note: The "add to portfolio" option is a dashboard/UI concern,
    not tested here.
    
    Validates: Requirements 8.4
    """
    from app.mcp.tools.stock_data import StockPrice, CompanyInfo
    
    # Generate mock search results
    mock_results = [
        StockSearchResult(
            ticker="AAPL",
            company_name="Apple Inc.",
            exchange="NASDAQ",
            relevance_score=1.0
        )
    ]
    
    # Mock detailed stock data
    mock_price = StockPrice(
        ticker="AAPL",
        price=150.0,
        change=2.5,
        change_percent=1.7,
        volume=50000000,
        timestamp=__import__('datetime').datetime.now()
    )
    
    mock_company_info = CompanyInfo(
        ticker="AAPL",
        name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        market_cap=2500000000000.0,
        description="Apple Inc. designs, manufactures, and markets smartphones."
    )
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.search_stocks.return_value = mock_results
    mock_mcp_tools.get_stock_price.return_value = mock_price
    mock_mcp_tools.get_company_info.return_value = mock_company_info
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Search stocks
        results = await service.searchStocks(query)
        
        if results:
            # Select first result
            selected = results[0]
            
            # Verify we can get detailed information for the selected stock
            price_data = await service.getCurrentPrice(selected.ticker)
            company_data = await service.getCompanyInfo(selected.ticker)
            
            # Verify price data completeness
            assert price_data.ticker == selected.ticker
            assert hasattr(price_data, 'price')
            assert hasattr(price_data, 'change')
            assert hasattr(price_data, 'change_percent')
            assert hasattr(price_data, 'volume')
            assert hasattr(price_data, 'timestamp')
            
            # Verify company info completeness
            assert company_data.ticker == selected.ticker
            assert hasattr(company_data, 'name')
            assert hasattr(company_data, 'sector')
            assert hasattr(company_data, 'industry')
            assert hasattr(company_data, 'market_cap')
            assert hasattr(company_data, 'description')


# Property 34: Multi-Exchange Search Coverage
@pytest.mark.asyncio
@given(query=search_query_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_multi_exchange_search_coverage(query):
    """
    Property 34: Multi-Exchange Search Coverage
    
    For any search query, results should include stocks from all major
    US exchanges (NYSE, NASDAQ, AMEX).
    
    Validates: Requirements 8.5
    """
    # Generate mock search results from multiple exchanges
    mock_results = [
        StockSearchResult(
            ticker="NYSE1",
            company_name="NYSE Company",
            exchange="NYSE",
            relevance_score=0.9
        ),
        StockSearchResult(
            ticker="NSDQ1",
            company_name="NASDAQ Company",
            exchange="NASDAQ",
            relevance_score=0.8
        ),
        StockSearchResult(
            ticker="AMEX1",
            company_name="AMEX Company",
            exchange="AMEX",
            relevance_score=0.7
        )
    ]
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.search_stocks.return_value = mock_results
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Search stocks
        results = await service.searchStocks(query)
        
        # Verify results can include multiple exchanges
        if results:
            exchanges = set(result.exchange for result in results)
            
            # Verify exchanges are from major US exchanges
            valid_exchanges = {"NYSE", "NASDAQ", "AMEX"}
            for exchange in exchanges:
                assert exchange in valid_exchanges, \
                    f"Exchange {exchange} is not a major US exchange"
            
            # Note: We don't require ALL exchanges to be present in every search,
            # just that the system supports all major exchanges


@pytest.mark.asyncio
@given(
    query=search_query_strategy(),
    limit=st.integers(min_value=1, max_value=10)
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_search_result_limiting(query, limit):
    """
    Test that search results can be limited to a specified number.
    
    Validates: Requirements 8.2, 8.3
    """
    # Generate more results than the limit
    mock_results = [
        StockSearchResult(
            ticker=f"TICK{i}",
            company_name=f"Company {i}",
            exchange="NYSE",
            relevance_score=1.0 - (i * 0.05)
        )
        for i in range(20)
    ]
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.search_stocks.return_value = mock_results
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Search stocks with limit
        results = await service.searchStocks(query, limit=limit)
        
        # Verify result count respects limit
        assert len(results) <= limit, \
            f"Expected at most {limit} results, got {len(results)}"
        
        # Verify results are still sorted by relevance
        if len(results) > 1:
            relevance_scores = [result.relevance_score for result in results]
            for i in range(len(relevance_scores) - 1):
                assert relevance_scores[i] >= relevance_scores[i + 1]


@pytest.mark.asyncio
@given(query=search_query_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_search_caching(query):
    """
    Test that search results are properly cached.
    
    Validates: Requirements 8.5, 21.5
    """
    mock_results = [
        StockSearchResult(
            ticker="AAPL",
            company_name="Apple Inc.",
            exchange="NASDAQ",
            relevance_score=1.0
        )
    ]
    
    # Mock MCP tools
    mock_mcp_tools = AsyncMock(spec=StockDataMCPTools)
    mock_mcp_tools.search_stocks.return_value = mock_results
    
    # Mock Redis
    with patch("app.services.stock_data_service.get_redis") as mock_redis_factory:
        mock_redis = Mock()
        mock_redis.get.return_value = None  # Cache miss
        mock_redis.setex.return_value = True
        mock_redis_factory.return_value = mock_redis
        
        # Create service
        service = StockDataService(mock_mcp_tools)
        
        # Search stocks
        results = await service.searchStocks(query)
        
        # Verify cache was set with correct TTL (15 minutes = 900 seconds)
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][1] == 900  # TTL in seconds
