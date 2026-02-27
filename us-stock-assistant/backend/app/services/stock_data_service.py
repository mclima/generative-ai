"""
Stock Data Service for retrieving stock prices, historical data, and company information.

This service provides caching and fallback logic for stock data retrieval via MCP.
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import json

from app.mcp.tools.stock_data import (
    StockDataMCPTools,
    StockPrice,
    HistoricalDataPoint,
    CompanyInfo,
    FinancialMetrics,
    StockSearchResult
)
from app.mcp.exceptions import MCPToolError, MCPConnectionError, MCPTimeoutError
from app.redis_client import get_redis

logger = logging.getLogger(__name__)


class StockDataService:
    """
    Service for retrieving stock data with caching and fallback logic.
    
    Implements:
    - Redis caching with 60-second TTL for prices
    - Redis caching with 1-hour TTL for historical data
    - Cache invalidation and fallback to last known valid data
    - Stock search with relevance ranking and result limiting
    - Company info and financial metrics retrieval
    """
    
    # Cache TTLs in seconds
    PRICE_CACHE_TTL = 60  # 60 seconds for real-time prices
    HISTORICAL_CACHE_TTL = 3600  # 1 hour for historical data
    SEARCH_CACHE_TTL = 900  # 15 minutes for search results
    COMPANY_INFO_CACHE_TTL = 86400  # 24 hours for company info
    FINANCIAL_METRICS_CACHE_TTL = 3600  # 1 hour for financial metrics
    
    def __init__(self, mcp_tools: StockDataMCPTools):
        """
        Initialize Stock Data Service.
        
        Args:
            mcp_tools: StockDataMCPTools instance for MCP communication
        """
        self.mcp_tools = mcp_tools
        self.redis = get_redis()
    
    def _get_price_cache_key(self, ticker: str) -> str:
        """Get Redis cache key for stock price."""
        return f"stock:price:{ticker.upper()}"
    
    def _get_historical_cache_key(self, ticker: str, start_date: date, end_date: date) -> str:
        """Get Redis cache key for historical data."""
        return f"stock:historical:{ticker.upper()}:{start_date.isoformat()}:{end_date.isoformat()}"
    
    def _get_search_cache_key(self, query: str) -> str:
        """Get Redis cache key for search results."""
        return f"stock:search:{query.lower()}"
    
    def _get_company_info_cache_key(self, ticker: str) -> str:
        """Get Redis cache key for company info."""
        return f"stock:company:{ticker.upper()}"
    
    def _get_financial_metrics_cache_key(self, ticker: str) -> str:
        """Get Redis cache key for financial metrics."""
        return f"stock:metrics:{ticker.upper()}"
    
    async def getCurrentPrice(self, ticker: str) -> StockPrice:
        """
        Get current stock price with caching and fallback logic.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            StockPrice with current price data
        
        Raises:
            ValueError: If ticker is invalid or data cannot be retrieved
        """
        ticker = ticker.upper()
        cache_key = self._get_price_cache_key(ticker)
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for price: {ticker}")
                data = json.loads(cached_data)
                return StockPrice(**data)
        except Exception as e:
            logger.warning(f"Failed to read from cache for {ticker}: {e}")
        
        # Fetch from MCP
        try:
            price_data = await self.mcp_tools.get_stock_price(ticker)
            
            # Cache the result
            try:
                self.redis.setex(
                    cache_key,
                    self.PRICE_CACHE_TTL,
                    json.dumps(price_data.dict())
                )
                logger.debug(f"Cached price for {ticker}")
            except Exception as e:
                logger.warning(f"Failed to cache price for {ticker}: {e}")
            
            return price_data
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting price for {ticker}: {e}")
            
            # Try to get last known valid price from cache (even if expired)
            try:
                # Try to get expired cache data
                cached_data = self.redis.get(cache_key)
                if cached_data:
                    logger.info(f"Using last known price for {ticker} due to MCP error")
                    data = json.loads(cached_data)
                    return StockPrice(**data)
            except Exception:
                pass
            
            # No fallback available
            raise ValueError(f"Unable to retrieve price for {ticker}: {str(e)}")

    async def getBatchPrices(self, tickers: List[str]) -> Dict[str, StockPrice]:
        """
        Get current prices for multiple stocks in parallel.
        
        Args:
            tickers: List of stock ticker symbols
        
        Returns:
            Dictionary mapping ticker to StockPrice
        """
        import asyncio
        
        async def fetch_price(ticker: str) -> tuple[str, Optional[StockPrice]]:
            try:
                price_data = await self.getCurrentPrice(ticker)
                return (ticker.upper(), price_data)
            except Exception as e:
                logger.warning(f"Failed to get price for {ticker}: {e}")
                return (ticker.upper(), None)
        
        # Fetch all prices in parallel
        price_results = await asyncio.gather(*[fetch_price(ticker) for ticker in tickers])
        
        # Filter out None results and build dictionary
        results = {ticker: price for ticker, price in price_results if price is not None}
        
        return results
    
    async def getHistoricalData(
        self,
        ticker: str,
        start_date: date,
        end_date: date
    ) -> List[HistoricalDataPoint]:
        """
        Get historical price data with caching.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date for historical data
            end_date: End date for historical data
        
        Returns:
            List of historical data points
        
        Raises:
            ValueError: If ticker is invalid or data cannot be retrieved
        """
        ticker = ticker.upper()
        cache_key = self._get_historical_cache_key(ticker, start_date, end_date)
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for historical data: {ticker}")
                data_list = json.loads(cached_data)
                return [HistoricalDataPoint(**item) for item in data_list]
        except Exception as e:
            logger.warning(f"Failed to read historical data from cache for {ticker}: {e}")
        
        # Fetch from MCP
        try:
            historical_data = await self.mcp_tools.get_historical_data(
                ticker, start_date, end_date
            )
            
            # Cache the result
            try:
                data_list = [item.dict() for item in historical_data]
                self.redis.setex(
                    cache_key,
                    self.HISTORICAL_CACHE_TTL,
                    json.dumps(data_list, default=str)
                )
                logger.debug(f"Cached historical data for {ticker}")
            except Exception as e:
                logger.warning(f"Failed to cache historical data for {ticker}: {e}")
            
            return historical_data
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting historical data for {ticker}: {e}")
            raise ValueError(f"Unable to retrieve historical data for {ticker}: {str(e)}")
    
    async def searchStocks(self, query: str, limit: Optional[int] = None) -> List[StockSearchResult]:
        """
        Search for stocks by ticker or company name with caching.
        
        Results are ranked by relevance and can be limited.
        
        Args:
            query: Search query (ticker or company name)
            limit: Maximum number of results to return (optional)
        
        Returns:
            List of stock search results, sorted by relevance
        """
        cache_key = self._get_search_cache_key(query)
        use_cache = len(query) >= 3
        
        # Try to get from cache (only for queries 3+ chars)
        try:
            cached_data = self.redis.get(cache_key) if use_cache else None
            if cached_data:
                logger.debug(f"Cache hit for search: {query}")
                data_list = json.loads(cached_data)
                query_upper = query.upper()
                results = []
                for item in data_list:
                    ticker = item.get("ticker", "")
                    if ticker.upper() == query_upper:
                        item["relevance_score"] = 3.0
                    elif ticker.upper().startswith(query_upper):
                        item["relevance_score"] = 2.0
                    else:
                        item["relevance_score"] = 1.0
                    results.append(StockSearchResult(**item))
                results.sort(key=lambda x: x.relevance_score, reverse=True)
                
                # Apply limit if specified
                if limit is not None and limit > 0:
                    results = results[:limit]
                
                return results
        except Exception as e:
            logger.warning(f"Failed to read search results from cache for '{query}': {e}")
        
        # Fetch from MCP
        try:
            search_results = await self.mcp_tools.search_stocks(query)
            
            # Cache the result (only for 3+ char queries with non-empty results)
            try:
                if use_cache and search_results:
                    data_list = [item.dict() for item in search_results]
                    self.redis.setex(
                        cache_key,
                        self.SEARCH_CACHE_TTL,
                        json.dumps(data_list)
                    )
                    logger.debug(f"Cached search results for '{query}'")
            except Exception as e:
                logger.warning(f"Failed to cache search results for '{query}': {e}")
            
            # Apply limit if specified
            if limit is not None and limit > 0:
                search_results = search_results[:limit]
            
            return search_results
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error searching stocks for '{query}': {e}")
            raise ValueError(f"Unable to search stocks for '{query}': {str(e)}")
    
    async def getCompanyInfo(self, ticker: str) -> CompanyInfo:
        """
        Get company information with caching.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            CompanyInfo with company details
        
        Raises:
            ValueError: If ticker is invalid or data cannot be retrieved
        """
        ticker = ticker.upper()
        cache_key = self._get_company_info_cache_key(ticker)
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for company info: {ticker}")
                data = json.loads(cached_data)
                return CompanyInfo(**data)
        except Exception as e:
            logger.warning(f"Failed to read company info from cache for {ticker}: {e}")
        
        # Fetch from MCP
        try:
            company_info = await self.mcp_tools.get_company_info(ticker)
            
            # Cache the result
            try:
                self.redis.setex(
                    cache_key,
                    self.COMPANY_INFO_CACHE_TTL,
                    json.dumps(company_info.dict())
                )
                logger.debug(f"Cached company info for {ticker}")
            except Exception as e:
                logger.warning(f"Failed to cache company info for {ticker}: {e}")
            
            return company_info
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting company info for {ticker}: {e}")
            raise ValueError(f"Unable to retrieve company info for {ticker}: {str(e)}")
    
    async def getFinancialMetrics(self, ticker: str) -> FinancialMetrics:
        """
        Get financial metrics with caching.
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            FinancialMetrics with financial data
        
        Raises:
            ValueError: If ticker is invalid or data cannot be retrieved
        """
        ticker = ticker.upper()
        cache_key = self._get_financial_metrics_cache_key(ticker)
        
        # Try to get from cache
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for financial metrics: {ticker}")
                data = json.loads(cached_data)
                return FinancialMetrics(**data)
        except Exception as e:
            logger.warning(f"Failed to read financial metrics from cache for {ticker}: {e}")
        
        # Fetch from MCP
        try:
            financial_metrics = await self.mcp_tools.get_financial_metrics(ticker)
            
            # Cache the result
            try:
                self.redis.setex(
                    cache_key,
                    self.FINANCIAL_METRICS_CACHE_TTL,
                    json.dumps(financial_metrics.dict())
                )
                logger.debug(f"Cached financial metrics for {ticker}")
            except Exception as e:
                logger.warning(f"Failed to cache financial metrics for {ticker}: {e}")
            
            return financial_metrics
        
        except (MCPToolError, MCPConnectionError, MCPTimeoutError) as e:
            logger.error(f"MCP error getting financial metrics for {ticker}: {e}")
            raise ValueError(f"Unable to retrieve financial metrics for {ticker}: {str(e)}")
    
    def invalidate_price_cache(self, ticker: str) -> None:
        """
        Invalidate cached price data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
        """
        cache_key = self._get_price_cache_key(ticker)
        try:
            self.redis.delete(cache_key)
            logger.info(f"Invalidated price cache for {ticker}")
        except Exception as e:
            logger.warning(f"Failed to invalidate price cache for {ticker}: {e}")
    
    def invalidate_all_caches(self, ticker: str) -> None:
        """
        Invalidate all cached data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
        """
        ticker = ticker.upper()
        
        # Invalidate price cache
        self.invalidate_price_cache(ticker)
        
        # Invalidate company info cache
        try:
            self.redis.delete(self._get_company_info_cache_key(ticker))
        except Exception as e:
            logger.warning(f"Failed to invalidate company info cache for {ticker}: {e}")
        
        # Invalidate financial metrics cache
        try:
            self.redis.delete(self._get_financial_metrics_cache_key(ticker))
        except Exception as e:
            logger.warning(f"Failed to invalidate financial metrics cache for {ticker}: {e}")
        
        logger.info(f"Invalidated all caches for {ticker}")
