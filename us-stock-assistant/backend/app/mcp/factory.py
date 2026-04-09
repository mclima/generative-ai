"""Factory for creating MCP clients."""

from typing import Dict
from functools import lru_cache

from app.config import get_settings
from .client import MCPClient
from .config import MCPConfig


class MCPClientFactory:
    """Factory for creating and managing MCP clients."""
    
    def __init__(self):
        self._clients: Dict[str, MCPClient] = {}
        self._settings = get_settings()

    @staticmethod
    def _require_server_url(server_url: str, env_var_name: str) -> str:
        """Validate that a required MCP server URL is configured."""
        normalized = (server_url or "").strip()
        if not normalized:
            raise ValueError(
                f"Missing required MCP server URL: set {env_var_name} in backend environment"
            )
        return normalized
    
    def get_stock_data_client(self) -> MCPClient:
        """Get or create stock data MCP client."""
        if "stock_data" not in self._clients:
            server_url = self._require_server_url(
                self._settings.mcp_stock_data_url,
                "MCP_STOCK_DATA_URL",
            )
            config = MCPConfig(
                server_url=server_url,
                timeout=30,
                retry_attempts=3,
                retry_delay=1.0,
                pool_size=10,
            )
            self._clients["stock_data"] = MCPClient(config)
        return self._clients["stock_data"]
    
    def get_news_client(self) -> MCPClient:
        """Get or create news MCP client."""
        if "news" not in self._clients:
            server_url = self._require_server_url(
                self._settings.mcp_news_url,
                "MCP_NEWS_URL",
            )
            config = MCPConfig(
                server_url=server_url,
                timeout=30,
                retry_attempts=3,
                retry_delay=1.0,
                pool_size=10,
            )
            self._clients["news"] = MCPClient(config)
        return self._clients["news"]
    
    def get_market_data_client(self) -> MCPClient:
        """Get or create market data MCP client."""
        if "market_data" not in self._clients:
            server_url = self._require_server_url(
                self._settings.mcp_market_data_url,
                "MCP_MARKET_DATA_URL",
            )
            config = MCPConfig(
                server_url=server_url,
                timeout=30,
                retry_attempts=3,
                retry_delay=1.0,
                pool_size=10,
            )
            self._clients["market_data"] = MCPClient(config)
        return self._clients["market_data"]
    
    async def close_all(self):
        """Close all MCP clients."""
        for client in self._clients.values():
            await client.disconnect()
        self._clients.clear()


@lru_cache()
def get_mcp_factory() -> MCPClientFactory:
    """Get singleton MCP client factory."""
    return MCPClientFactory()
