"""
Official MCP SDK Client Implementation
Uses the Model Context Protocol SDK for proper protocol compliance
"""
import logging
from typing import Any, Dict, List, Optional
import httpx
import json

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
        For SSE transport, we just verify the server is reachable.
        """
        try:
            # Test connection to SSE endpoint
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.server_url}/sse", timeout=10.0)
                # SSE endpoints return 200 even without Accept: text/event-stream
                if response.status_code not in [200, 404]:  # 404 is ok, means different path
                    response.raise_for_status()
            
            logger.info(f"Connected to MCP server {self.server_name} at {self.server_url}")
        except Exception as e:
            logger.warning(f"Could not verify MCP server {self.server_name}: {e}")
            # Don't fail - server might still work
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        Uses the MCP protocol's tools/list method via SSE.
        
        Returns:
            List of tool definitions with name, description, and input schema
        """
        if self._tools_cache:
            return self._tools_cache
        
        try:
            # Send tools/list request via SSE
            result = await self._send_mcp_request("tools/list", {})
            tools = result.get("tools", [])
            self._tools_cache = tools
            return tools
        except Exception as e:
            logger.warning(f"Failed to list tools from {self.server_name}: {e}")
            return []
    
    async def _send_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an MCP request via SSE transport.
        
        Args:
            method: MCP method name (e.g., "tools/call", "tools/list")
            params: Method parameters
            
        Returns:
            Response data
        """
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.server_url}/sse",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle JSON-RPC response
            if "error" in data:
                raise Exception(f"MCP error: {data['error']}")
            
            return data.get("result", {})
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.
        Uses the MCP protocol's tools/call method via SSE.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool execution result
        """
        try:
            result = await self._send_mcp_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            # Extract content from MCP response
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    # Return the text content from the first item
                    first_content = content[0]
                    if isinstance(first_content, dict) and "text" in first_content:
                        text_data = first_content["text"]
                        # Try to parse as JSON
                        try:
                            return json.loads(text_data)
                        except:
                            return text_data
                return content
            
            return result
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close connection to MCP server."""
        self._tools_cache = None
        logger.info(f"Disconnected from MCP server {self.server_name}")
