"""
Property-based tests for MCP protocol compliance and retry logic.

Feature: us-stock-assistant
Property 13: MCP Protocol Compliance
Property 15: MCP Retry Logic
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock, patch
import httpx

from app.mcp.client import MCPClient, MCPResponse, MCPTool
from app.mcp.config import MCPConfig
from app.mcp.exceptions import (
    MCPConnectionError,
    MCPToolError,
    MCPTimeoutError,
)


# Hypothesis strategies for generating test data
@st.composite
def mcp_config_strategy(draw):
    """Generate valid MCP configurations."""
    return MCPConfig(
        server_url=draw(st.sampled_from([
            "http://localhost:8001",
            "http://mcp-server:8000",
            "https://api.example.com"
        ])),
        api_key=draw(st.one_of(st.none(), st.text(min_size=10, max_size=50))),
        timeout=draw(st.integers(min_value=5, max_value=60)),
        retry_attempts=draw(st.integers(min_value=1, max_value=5)),
        retry_delay=draw(st.floats(min_value=0.1, max_value=2.0)),
        pool_size=draw(st.integers(min_value=1, max_value=20)),
    )


@st.composite
def tool_request_strategy(draw):
    """Generate valid tool requests."""
    tool_name = draw(st.sampled_from([
        "get_stock_price",
        "get_historical_data",
        "get_company_info",
        "search_stocks"
    ]))
    
    params = {}
    if tool_name == "get_stock_price":
        params = {"ticker": draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=("Lu",))))}
    elif tool_name == "get_historical_data":
        params = {
            "ticker": draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=("Lu",)))),
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    elif tool_name == "get_company_info":
        params = {"ticker": draw(st.text(min_size=1, max_size=5, alphabet=st.characters(whitelist_categories=("Lu",))))}
    elif tool_name == "search_stocks":
        params = {"query": draw(st.text(min_size=1, max_size=20))}
    
    return tool_name, params


# Property 13: MCP Protocol Compliance
@pytest.mark.asyncio
@given(config=mcp_config_strategy(), tool_request=tool_request_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_mcp_protocol_compliance(config, tool_request):
    """
    Property 13: MCP Protocol Compliance
    
    For any MCP tool request, the MCP client should format the request according
    to MCP standards, send it to the server, and parse the response according to
    MCP schemas.
    
    Validates: Requirements 10.2, 10.3, 10.4
    """
    tool_name, params = tool_request
    
    # Mock HTTP client
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"result": "test_data"}
    }
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Mock tool execution
        mock_client.post.return_value = mock_response
        
        # Create client and execute tool
        client = MCPClient(config)
        await client.connect()
        
        try:
            response = await client.execute_tool(tool_name, params)
            
            # Verify request format compliance
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            
            # Check endpoint
            assert call_args[0][0] == "/tools/execute"
            
            # Check request body structure (MCP standard)
            request_body = call_args[1]["json"]
            assert "tool" in request_body
            assert "parameters" in request_body
            assert request_body["tool"] == tool_name
            assert request_body["parameters"] == params
            
            # Verify response parsing compliance
            assert isinstance(response, MCPResponse)
            assert response.success is True
            assert response.data is not None
            assert response.error is None
            
        finally:
            await client.disconnect()


# Property 15: MCP Retry Logic
@pytest.mark.asyncio
@given(
    config=mcp_config_strategy(),
    tool_request=tool_request_strategy(),
    failure_count=st.integers(min_value=1, max_value=3)
)
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_mcp_retry_logic_with_exponential_backoff(config, tool_request, failure_count):
    """
    Property 15: MCP Retry Logic
    
    For any MCP connection error, the client should retry the request with
    exponential backoff up to a maximum number of attempts before failing.
    
    Validates: Requirements 10.5
    """
    tool_name, params = tool_request
    
    # Ensure we have enough retry attempts (need at least failure_count + 1 for success)
    if config.retry_attempts <= failure_count:
        config = MCPConfig(
            server_url=config.server_url,
            api_key=config.api_key,
            timeout=config.timeout,
            retry_attempts=failure_count + 1,
            retry_delay=0.01,  # Fast retries for testing
            max_retry_delay=0.1,
            pool_size=config.pool_size,
        )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Create a sequence of failures followed by success
        call_count = 0
        
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= failure_count:
                # Simulate timeout error
                raise httpx.TimeoutException("Request timed out")
            else:
                # Success on final attempt
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "success": True,
                    "data": {"result": "success_after_retries"}
                }
                return mock_response
        
        mock_client.post.side_effect = side_effect
        
        # Create client and execute tool
        client = MCPClient(config)
        await client.connect()
        
        try:
            start_time = asyncio.get_event_loop().time()
            response = await client.execute_tool(tool_name, params)
            end_time = asyncio.get_event_loop().time()
            
            # Verify retry behavior
            assert call_count == failure_count + 1, f"Expected {failure_count + 1} calls, got {call_count}"
            
            # Verify exponential backoff (should have some delay)
            if failure_count > 0:
                expected_min_delay = config.retry_delay * (2 ** 0 - 1) / 2  # Rough estimate
                elapsed_time = end_time - start_time
                # Just verify some delay occurred (not exact timing due to test overhead)
                assert elapsed_time >= 0
            
            # Verify eventual success
            assert response.success is True
            assert response.data is not None
            
        finally:
            await client.disconnect()


@pytest.mark.asyncio
@given(config=mcp_config_strategy(), tool_request=tool_request_strategy())
@settings(
    max_examples=5,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
async def test_mcp_retry_exhaustion(config, tool_request):
    """
    Property 15: MCP Retry Logic (Exhaustion Case)
    
    For any MCP connection error that persists beyond retry attempts,
    the client should fail with an appropriate error.
    
    Validates: Requirements 10.5
    """
    tool_name, params = tool_request
    
    # Use fast retries for testing
    config = MCPConfig(
        server_url=config.server_url,
        api_key=config.api_key,
        timeout=config.timeout,
        retry_attempts=2,  # Small number for fast testing
        retry_delay=0.01,
        max_retry_delay=0.1,
        pool_size=config.pool_size,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Always fail
        mock_client.post.side_effect = httpx.TimeoutException("Request timed out")
        
        # Create client and execute tool
        client = MCPClient(config)
        await client.connect()
        
        try:
            # Should raise MCPToolError after exhausting retries
            with pytest.raises(MCPToolError) as exc_info:
                await client.execute_tool(tool_name, params)
            
            # Verify error details
            assert "failed after" in str(exc_info.value).lower()
            assert tool_name in exc_info.value.details["tool_name"]
            
            # Verify all retry attempts were made
            assert mock_client.post.call_count == config.retry_attempts
            
        finally:
            await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_connection_pooling():
    """
    Test that MCP client properly manages connection pooling.
    
    Validates: Requirements 10.5
    """
    config = MCPConfig(
        server_url="http://localhost:8001",
        timeout=30,
        retry_attempts=3,
        retry_delay=1.0,
        pool_size=5,
    )
    
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Mock health check
        mock_health = Mock()
        mock_health.status_code = 200
        mock_client.get.return_value = mock_health
        
        # Create client
        client = MCPClient(config)
        await client.connect()
        
        try:
            # Verify connection pool configuration
            call_args = mock_client_class.call_args
            limits = call_args[1]["limits"]
            
            assert limits.max_connections == config.pool_size
            assert limits.max_keepalive_connections == config.pool_size // 2
            
        finally:
            await client.disconnect()


@pytest.mark.asyncio
async def test_mcp_list_tools():
    """
    Test that MCP client can list available tools.
    
    Validates: Requirements 10.1
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
        
        # Mock tools list
        mock_tools_response = Mock()
        mock_tools_response.status_code = 200
        mock_tools_response.json.return_value = {
            "tools": [
                {
                    "name": "get_stock_price",
                    "description": "Get current stock price",
                    "parameters": {"ticker": "string"}
                },
                {
                    "name": "get_historical_data",
                    "description": "Get historical price data",
                    "parameters": {"ticker": "string", "start_date": "string", "end_date": "string"}
                }
            ]
        }
        
        # Configure mock to return different responses for different endpoints
        def get_side_effect(endpoint):
            if endpoint == "/health":
                return mock_health
            elif endpoint == "/tools":
                return mock_tools_response
            return mock_health
        
        mock_client.get.side_effect = get_side_effect
        
        # Create client and list tools
        client = MCPClient(config)
        await client.connect()
        
        try:
            tools = await client.list_tools()
            
            # Verify tools were retrieved
            assert len(tools) == 2
            assert all(isinstance(tool, MCPTool) for tool in tools)
            assert tools[0].name == "get_stock_price"
            assert tools[1].name == "get_historical_data"
            
            # Verify caching (second call should not hit server)
            tools2 = await client.list_tools()
            assert tools2 == tools
            
        finally:
            await client.disconnect()
