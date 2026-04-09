"""
Official MCP SDK Client Implementation
Uses the Model Context Protocol SDK for proper protocol compliance
"""
import logging
from typing import Any, Dict, List, Optional
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

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
        self._session_context = None
        self._tools_cache: Optional[List[Dict[str, Any]]] = None
        self._read_stream = None
        self._write_stream = None
        self._streams_context = None

    def _get_sse_url(self) -> str:
        """Build SSE endpoint URL, supporting base URL or explicit /sse URL."""
        base = (self.server_url or "").rstrip("/")
        if not base:
            raise ValueError(f"MCP server URL is empty for {self.server_name}")
        return base if base.endswith("/sse") else f"{base}/sse"
        
    async def connect(self) -> None:
        """
        Connect to the MCP server using official MCP SDK.
        """
        try:
            # Use official MCP SDK SSE client as context manager
            # The sse_client expects the full SSE endpoint URL.
            sse_url = self._get_sse_url()
            self._streams_context = sse_client(sse_url)
            self._read_stream, self._write_stream = await self._streams_context.__aenter__()
            
            # Create ClientSession with the streams and enter context
            # to ensure background message handling lifecycle is managed.
            self._session_context = ClientSession(self._read_stream, self._write_stream)
            self._session = await self._session_context.__aenter__()
            
            # Initialize the session
            await self._session.initialize()
            
            logger.info(f"Connected to MCP server {self.server_name} via SSE")
            
        except Exception as e:
            logger.error(
                f"Failed to connect to MCP server {self.server_name} at {self.server_url}: {e}"
            )
            await self.disconnect()
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            List of tool definitions with name, description, and input schema
        """
        if self._tools_cache:
            return self._tools_cache
        
        if not self._session:
            raise Exception("Not connected to MCP server")
        
        try:
            # Use official SDK to list tools
            result = await self._session.list_tools()
            
            # Convert to dict format
            tools = []
            for tool in result.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            self._tools_cache = tools
            logger.info(f"Listed {len(tools)} tools from {self.server_name}")
            return tools
            
        except Exception as e:
            logger.warning(f"Failed to list tools from {self.server_name}: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server using official SDK.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool execution result
        """
        if not self._session:
            raise Exception("Not connected to MCP server")
        
        try:
            # Use official SDK to call tool
            result = await self._session.call_tool(tool_name, arguments)
            
            # Extract content from MCP response
            if result.content:
                # Get first content item
                first_content = result.content[0]
                if hasattr(first_content, 'text'):
                    text_data = first_content.text
                    # Try to parse as JSON
                    try:
                        import json
                        return json.loads(text_data)
                    except Exception:
                        # FastMCP may return Python-literal-like payload strings
                        # (single quotes) that are not strict JSON.
                        try:
                            import ast
                            return ast.literal_eval(text_data)
                        except Exception:
                            return text_data
                return first_content
            
            return None
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        if self._streams_context:
            try:
                await self._streams_context.__aexit__(None, None, None)
            except Exception:
                pass

        self._session = None
        self._session_context = None
        self._streams_context = None

        self._read_stream = None
        self._write_stream = None
        self._tools_cache = None
        logger.info(f"Disconnected from MCP server {self.server_name}")
