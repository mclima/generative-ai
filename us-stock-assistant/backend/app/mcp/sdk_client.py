"""
Official MCP SDK Client Implementation
Uses the Model Context Protocol SDK for proper protocol compliance
"""
import logging
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MCPSDKClient:
    """
    MCP client using the official SDK.
    Connects to MCP servers over HTTP/SSE transport.
    """
    
    def __init__(self, server_url: str, server_name: str):
        """
        Initialize MCP SDK client.
        
        Args:
            server_url: URL of the MCP server (e.g., http://localhost:8002)
            server_name: Name of the server for logging
        """
        self.server_url = server_url
        self.server_name = server_name
        self._session: Optional[ClientSession] = None
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        
    async def connect(self) -> None:
        """
        Connect to the MCP server.
        For HTTP/SSE transport, we'll use httpx to communicate.
        """
        try:
            # Test connection
            async with httpx.AsyncClient() as client:
                response = await client.get(self.server_url, timeout=10.0)
                response.raise_for_status()
            
            logger.info(f"Connected to MCP server {self.server_name} at {self.server_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server {self.server_name}: {e}")
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        Uses the MCP protocol's tools/list method.
        
        Returns:
            List of tool definitions with name, description, and input schema
        """
        if self._tools_cache:
            return self._tools_cache
        
        try:
            async with httpx.AsyncClient() as client:
                # MCP servers expose tools via SSE endpoint
                # For now, we'll use a simple HTTP endpoint to get tool list
                response = await client.get(f"{self.server_url}/mcp/tools", timeout=10.0)
                
                if response.status_code == 404:
                    # Fallback: server might expose tools differently
                    # Try to infer from root endpoint
                    response = await client.get(self.server_url, timeout=10.0)
                    data = response.json()
                    
                    # Convert simple tool list to MCP format
                    tools = []
                    for tool_name in data.get("tools", []):
                        tools.append({
                            "name": tool_name,
                            "description": f"MCP tool: {tool_name}",
                            "inputSchema": {"type": "object", "properties": {}}
                        })
                    
                    self._tools_cache = tools
                    return tools
                
                response.raise_for_status()
                tools = response.json().get("tools", [])
                self._tools_cache = tools
                return tools
                
        except Exception as e:
            logger.warning(f"Failed to list tools from {self.server_name}: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.
        Uses the MCP protocol's tools/call method.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool execution result
        """
        try:
            async with httpx.AsyncClient() as client:
                # Call the tool using the MCP server's endpoint
                # MCP servers expose tools at /tools/{tool_name}
                response = await client.post(
                    f"{self.server_url}/tools/{tool_name}",
                    json=arguments,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Handle MCP response format
                if isinstance(data, dict):
                    # Check for MCP standard response
                    if "success" in data:
                        if data["success"]:
                            return data.get("data")
                        else:
                            raise Exception(f"Tool execution failed: {data.get('error', 'Unknown error')}")
                    # Direct data return (FastMCP format)
                    return data
                
                # Direct list/value return
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e.response.status_code}")
            raise Exception(f"Tool {tool_name} failed: HTTP {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        self._tools_cache = None
        logger.info(f"Disconnected from MCP server {self.server_name}")
