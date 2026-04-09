"""Test MCP connection directly"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.mcp.sdk_client import MCPSDKClient

async def test_connection():
    # Test stock data server
    client = MCPSDKClient("http://localhost:8001", "stock-data-server")
    
    print("Connecting to MCP server...")
    await client.connect()
    
    print(f"Session endpoint: {client._session_endpoint}")
    
    print("\nListing tools...")
    tools = await client.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.get('name')}")
    
    print("\nCalling get_stock_price for AAPL...")
    result = await client.call_tool("get_stock_price", {"ticker": "AAPL"})
    print(f"Result: {result}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_connection())
