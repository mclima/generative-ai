"""MCP client implementation with connection pooling and retry logic."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx

from .config import MCPConfig
from .exceptions import (
    MCPConnectionError,
    MCPToolError,
    MCPTimeoutError,
    MCPValidationError,
)

logger = logging.getLogger(__name__)


class MCPResponse:
    """MCP response wrapper."""
    
    def __init__(self, success: bool, data: Any = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = datetime.utcnow()
    
    def __repr__(self):
        return f"MCPResponse(success={self.success}, error={self.error})"


class MCPTool:
    """MCP tool definition."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def __repr__(self):
        return f"MCPTool(name={self.name})"


class MCPClient:
    """
    MCP client with connection pooling and retry logic.
    
    Implements exponential backoff for retries and maintains a connection pool
    for efficient resource usage.
    """
    
    def __init__(self, config: MCPConfig):
        """
        Initialize MCP client.
        
        Args:
            config: MCP configuration
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._connected = False
        self._tools_cache: Optional[List[MCPTool]] = None
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """
        Establish connection to MCP server.
        
        Raises:
            MCPConnectionError: If connection fails
        """
        async with self._lock:
            if self._connected:
                return
            
            try:
                # Create HTTP client with connection pooling
                limits = httpx.Limits(
                    max_connections=self.config.pool_size,
                    max_keepalive_connections=self.config.pool_size // 2,
                )
                
                timeout = httpx.Timeout(self.config.timeout)
                
                headers = {}
                if self.config.api_key:
                    headers["Authorization"] = f"Bearer {self.config.api_key}"
                
                self._client = httpx.AsyncClient(
                    base_url=self.config.server_url,
                    headers=headers,
                    limits=limits,
                    timeout=timeout,
                )
                
                # Test connection
                await self._test_connection()
                
                self._connected = True
                logger.info(f"Connected to MCP server at {self.config.server_url}")
                
            except Exception as e:
                logger.error(f"Failed to connect to MCP server: {e}")
                raise MCPConnectionError(
                    f"Failed to connect to MCP server: {str(e)}",
                    details={"server_url": self.config.server_url}
                )
    
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        async with self._lock:
            if self._client:
                await self._client.aclose()
                self._client = None
            self._connected = False
            self._tools_cache = None
            logger.info("Disconnected from MCP server")
    
    async def _test_connection(self) -> None:
        """
        Test connection to MCP server.
        
        Raises:
            MCPConnectionError: If connection test fails
        """
        try:
            response = await self._client.get("/")
            response.raise_for_status()
        except Exception as e:
            raise MCPConnectionError(f"Connection test failed: {str(e)}")
    
    async def execute_tool(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> MCPResponse:
        """
        Execute a tool on the MCP server with retry logic.
        
        Args:
            tool_name: Name of the tool to execute
            params: Tool parameters
        
        Returns:
            MCPResponse with tool execution result
        
        Raises:
            MCPConnectionError: If not connected
            MCPToolError: If tool execution fails after retries
        """
        if not self._connected:
            await self.connect()
        
        return await self._execute_with_retry(tool_name, params)
    
    async def _execute_with_retry(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> MCPResponse:
        """
        Execute tool with exponential backoff retry logic.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
        
        Returns:
            MCPResponse
        
        Raises:
            MCPToolError: If all retries fail
        """
        last_error = None
        delay = self.config.retry_delay
        
        for attempt in range(self.config.retry_attempts):
            try:
                return await self._execute_tool_request(tool_name, params)
            
            except MCPTimeoutError as e:
                last_error = e
                logger.warning(
                    f"Tool {tool_name} timed out (attempt {attempt + 1}/{self.config.retry_attempts})"
                )
            
            except MCPConnectionError as e:
                last_error = e
                logger.warning(
                    f"Connection error for tool {tool_name} (attempt {attempt + 1}/{self.config.retry_attempts})"
                )
                # Try to reconnect
                try:
                    await self.disconnect()
                    await self.connect()
                except Exception:
                    pass
            
            except MCPToolError as e:
                # Don't retry on tool errors (invalid parameters, etc.)
                raise e
            
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Unexpected error for tool {tool_name} (attempt {attempt + 1}/{self.config.retry_attempts}): {e}"
                )
            
            # Wait before retry with exponential backoff
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(min(delay, self.config.max_retry_delay))
                delay *= 2  # Exponential backoff
        
        # All retries failed
        error_msg = f"Tool {tool_name} failed after {self.config.retry_attempts} attempts"
        logger.error(f"{error_msg}: {last_error}")
        raise MCPToolError(
            error_msg,
            details={
                "tool_name": tool_name,
                "params": params,
                "last_error": str(last_error)
            }
        )
    
    async def _execute_tool_request(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> MCPResponse:
        """
        Execute a single tool request.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
        
        Returns:
            MCPResponse
        
        Raises:
            MCPTimeoutError: If request times out
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self._client.post(
                f"/tools/{tool_name}",
                json=params
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Validate response structure
            if "success" not in data:
                raise MCPValidationError("Response missing 'success' field")
            
            if data["success"]:
                return MCPResponse(
                    success=True,
                    data=data.get("data")
                )
            else:
                return MCPResponse(
                    success=False,
                    error=data.get("error", "Unknown error")
                )
        
        except httpx.TimeoutException as e:
            raise MCPTimeoutError(f"Tool {tool_name} timed out: {str(e)}")
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                raise MCPConnectionError(f"Server error: {e.response.status_code}")
            else:
                raise MCPToolError(
                    f"Tool execution failed: {e.response.status_code}",
                    details={"status_code": e.response.status_code}
                )
        
        except Exception as e:
            raise MCPToolError(f"Tool execution failed: {str(e)}")
    
    async def list_tools(self) -> List[MCPTool]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of available tools
        
        Raises:
            MCPConnectionError: If not connected
        """
        if not self._connected:
            await self.connect()
        
        # Return cached tools if available
        if self._tools_cache is not None:
            return self._tools_cache
        
        try:
            response = await self._client.get("/tools")
            response.raise_for_status()
            data = response.json()
            
            tools = []
            for tool_data in data.get("tools", []):
                tool = MCPTool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    parameters=tool_data.get("parameters", {})
                )
                tools.append(tool)
            
            self._tools_cache = tools
            logger.info(f"Retrieved {len(tools)} tools from MCP server")
            return tools
        
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise MCPConnectionError(f"Failed to list tools: {str(e)}")
    
    async def handle_error(self, error: Exception) -> None:
        """
        Handle MCP errors with appropriate recovery actions.
        
        Args:
            error: The error to handle
        """
        if isinstance(error, MCPConnectionError):
            logger.error(f"Connection error: {error.message}")
            # Try to reconnect
            try:
                await self.disconnect()
                await self.connect()
                logger.info("Reconnected to MCP server")
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
        
        elif isinstance(error, MCPToolError):
            logger.error(f"Tool error: {error.message}")
            # Tool errors are not recoverable, just log
        
        elif isinstance(error, MCPTimeoutError):
            logger.error(f"Timeout error: {error.message}")
            # Timeouts might be recoverable with retry
        
        else:
            logger.error(f"Unexpected error: {error}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
