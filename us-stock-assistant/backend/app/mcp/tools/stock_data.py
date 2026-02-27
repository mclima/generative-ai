"""Stock Data MCP Server tools wrapper."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

from app.mcp.client import MCPClient, MCPResponse
from app.mcp.exceptions import MCPToolError, MCPValidationError

logger = logging.getLogger(__name__)


# Response models for validation
class StockPrice(BaseModel):
    """Stock price data."""
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v


class HistoricalDataPoint(BaseModel):
    """Historical price data point."""
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    
    @validator('open', 'high', 'low', 'close')
    def validate_prices(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v
    
    @validator('volume')
    def validate_volume(cls, v):
        if v < 0:
            raise ValueError("Volume cannot be negative")
        return v


class CompanyInfo(BaseModel):
    """Company information."""
    ticker: str
    name: str
    sector: str
    industry: str
    market_cap: float
    description: str


class FinancialMetrics(BaseModel):
    """Financial metrics."""
    ticker: str
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None


class StockSearchResult(BaseModel):
    """Stock search result."""
    ticker: str
    company_name: str
    exchange: str
    relevance_score: float = Field(ge=0.0)


class MarketIndex(BaseModel):
    """Market index data."""
    name: str
    symbol: str
    value: float
    change: float
    change_percent: float


class StockDataMCPTools:
    """
    Wrapper for Stock Data MCP Server tools.
    
    Provides methods for retrieving stock prices, historical data,
    company information, financial metrics, and market indices.
    """
    
    def __init__(self, client: MCPClient):
        """
        Initialize Stock Data MCP Tools.
        
        Args:
            client: MCP client instance
        """
        self.client = client
    
    async def get_stock_price(self, ticker: str) -> StockPrice:
        """
        Get current stock price.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            StockPrice with current price data
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_stock_price",
                {"ticker": ticker.upper()}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get stock price for {ticker}: {response.error}",
                    details={"ticker": ticker, "error": response.error}
                )
            
            # Validate and parse response
            try:
                d = response.data
                return StockPrice(
                    ticker=d.get("ticker", ticker),
                    price=d.get("price", 0),
                    change=d.get("change", 0),
                    change_percent=d.get("change_percent") or d.get("changePercent", 0),
                    volume=d.get("volume", 0),
                    timestamp=d.get("timestamp", "")
                )
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for stock price: {str(e)}",
                    details={"ticker": ticker, "data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting stock price for {ticker}: {e}")
            raise MCPToolError(
                f"Unexpected error getting stock price: {str(e)}",
                details={"ticker": ticker}
            )
    
    async def get_historical_data(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[HistoricalDataPoint]:
        """
        Get historical price data.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
        
        Returns:
            List of historical data points
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_historical_data",
                {
                    "ticker": ticker.upper(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get historical data for {ticker}: {response.error}",
                    details={
                        "ticker": ticker,
                        "start_date": start_date,
                        "end_date": end_date,
                        "error": response.error
                    }
                )
            
            # Validate and parse response
            try:
                data_points = []
                for item in response.data:
                    data_points.append(HistoricalDataPoint(**item))
                
                # Sort by date
                data_points.sort(key=lambda x: x.date)
                return data_points
            
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for historical data: {str(e)}",
                    details={"ticker": ticker, "data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting historical data for {ticker}: {e}")
            raise MCPToolError(
                f"Unexpected error getting historical data: {str(e)}",
                details={"ticker": ticker}
            )
    
    async def get_company_info(self, ticker: str) -> CompanyInfo:
        """
        Get company information.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            CompanyInfo with company details
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_company_info",
                {"ticker": ticker.upper()}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get company info for {ticker}: {response.error}",
                    details={"ticker": ticker, "error": response.error}
                )
            
            # Validate and parse response (map camelCase to snake_case)
            try:
                d = response.data
                return CompanyInfo(
                    ticker=d.get("ticker", ticker),
                    name=d.get("name", ""),
                    sector=d.get("sector", ""),
                    industry=d.get("industry", ""),
                    market_cap=d.get("marketCap") or d.get("market_cap") or 0.0,
                    description=d.get("description", ""),
                )
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for company info: {str(e)}",
                    details={"ticker": ticker, "data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting company info for {ticker}: {e}")
            raise MCPToolError(
                f"Unexpected error getting company info: {str(e)}",
                details={"ticker": ticker}
            )
    
    async def get_financial_metrics(self, ticker: str) -> FinancialMetrics:
        """
        Get financial metrics.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            FinancialMetrics with financial data
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_financial_metrics",
                {"ticker": ticker.upper()}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get financial metrics for {ticker}: {response.error}",
                    details={"ticker": ticker, "error": response.error}
                )
            
            # Validate and parse response (map camelCase to snake_case)
            try:
                d = response.data
                return FinancialMetrics(
                    ticker=d.get("ticker", ticker),
                    pe_ratio=d.get("peRatio") or d.get("pe_ratio"),
                    eps=d.get("eps"),
                    dividend_yield=d.get("dividendYield") or d.get("dividend_yield"),
                    beta=d.get("beta"),
                    fifty_two_week_high=d.get("fiftyTwoWeekHigh") or d.get("fifty_two_week_high"),
                    fifty_two_week_low=d.get("fiftyTwoWeekLow") or d.get("fifty_two_week_low"),
                )
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for financial metrics: {str(e)}",
                    details={"ticker": ticker, "data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting financial metrics for {ticker}: {e}")
            raise MCPToolError(
                f"Unexpected error getting financial metrics: {str(e)}",
                details={"ticker": ticker}
            )
    
    async def search_stocks(self, query: str) -> List[StockSearchResult]:
        """
        Search for stocks by ticker or company name.
        
        Args:
            query: Search query
        
        Returns:
            List of stock search results
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "search_stocks",
                {"query": query}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to search stocks for '{query}': {response.error}",
                    details={"query": query, "error": response.error}
                )
            
            # Validate and parse response
            try:
                results = []
                query_upper = query.upper()
                for item in response.data:
                    ticker = item.get("ticker", "")
                    # Boost exact ticker match to 3.0, prefix match to 2.0, else 1.0
                    if ticker.upper() == query_upper:
                        score = 3.0
                    elif ticker.upper().startswith(query_upper):
                        score = 2.0
                    else:
                        score = 1.0
                    results.append(StockSearchResult(
                        ticker=ticker,
                        company_name=item.get("company_name") or item.get("companyName", ""),
                        exchange=item.get("exchange", ""),
                        relevance_score=score
                    ))
                
                # Sort by relevance score (descending)
                results.sort(key=lambda x: x.relevance_score, reverse=True)
                return results
            
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for stock search: {str(e)}",
                    details={"query": query, "data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching stocks for '{query}': {e}")
            raise MCPToolError(
                f"Unexpected error searching stocks: {str(e)}",
                details={"query": query}
            )
    
    async def get_market_indices(self) -> List[MarketIndex]:
        """
        Get major market indices (S&P 500, NASDAQ, DOW).
        
        Returns:
            List of market indices
        
        Raises:
            MCPToolError: If tool execution fails
            MCPValidationError: If response validation fails
        """
        try:
            response = await self.client.execute_tool(
                "get_market_indices",
                {}
            )
            
            if not response.success:
                raise MCPToolError(
                    f"Failed to get market indices: {response.error}",
                    details={"error": response.error}
                )
            
            # Validate and parse response
            try:
                indices = []
                for item in response.data:
                    indices.append(MarketIndex(
                        name=item.get("name", ""),
                        symbol=item.get("symbol", ""),
                        value=item.get("value", 0),
                        change=item.get("change", 0),
                        change_percent=item.get("change_percent") or item.get("changePercent", 0)
                    ))
                return indices
            
            except Exception as e:
                raise MCPValidationError(
                    f"Invalid response format for market indices: {str(e)}",
                    details={"data": response.data}
                )
        
        except (MCPToolError, MCPValidationError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting market indices: {e}")
            raise MCPToolError(
                f"Unexpected error getting market indices: {str(e)}"
            )
