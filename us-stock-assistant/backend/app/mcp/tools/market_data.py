"""Market Data MCP Server tools wrapper."""

import logging
from typing import List
from pydantic import BaseModel

from app.mcp.client import MCPClient
from app.mcp.exceptions import MCPToolError, MCPValidationError

logger = logging.getLogger(__name__)


class SectorPerformance(BaseModel):
    """Sector performance data."""
    sector: str
    change_percent: float
    top_performers: List[str]
    bottom_performers: List[str]


class MarketSentiment(BaseModel):
    """Market sentiment data."""
    overall_sentiment: str  # 'positive', 'negative', 'neutral'
    sentiment_score: float  # -1 to 1
    confidence: float  # 0 to 1


class MarketDataMCPTools:
    """
    Wrapper for Market Data MCP Server tools.
    
    Provides methods for retrieving sector performance and market sentiment.
    """
    
    def __init__(self, client: MCPClient):
        """
        Initialize Market Data MCP Tools.
        
        Args:
            client: MCP client instance
        """
        self.client = client
    
    async def get_sector_performance(self) -> List[SectorPerformance]:
        """
        Get performance data for market sectors.
        
        Returns:
            List of sector performance data
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_sector_performance",
                {}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get sector performance: {response.error}",
                    details={"error": response.error}
                )
            
            # Validate and parse response
            try:
                sectors = []
                for item in response.data:
                    sectors.append(SectorPerformance(**item))
                return sectors
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for sector performance: {str(e)}",
                    details={"data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting sector performance: {e}")
            raise MCPToolError(
                f"Unexpected error getting sector performance: {str(e)}"
            )
    
    async def get_market_sentiment(self) -> MarketSentiment:
        """
        Get aggregated market sentiment metrics.
        
        Returns:
            Market sentiment data
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_market_sentiment",
                {}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get market sentiment: {response.error}",
                    details={"error": response.error}
                )
            
            # Validate and parse response
            try:
                return MarketSentiment(**response.data)
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for market sentiment: {str(e)}",
                    details={"data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting market sentiment: {e}")
            raise MCPToolError(
                f"Unexpected error getting market sentiment: {str(e)}"
            )
