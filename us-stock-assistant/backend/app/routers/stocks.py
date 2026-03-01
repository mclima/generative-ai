"""
Stock data API endpoints.
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

from app.services.stock_data_service import StockDataService
from app.mcp.tools.stock_data import StockDataMCPTools
from app.validators import validate_search_query, validate_ticker
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/stocks", tags=["stocks"])
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class StockPriceResponse(BaseModel):
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str


class HistoricalDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockSearchResult(BaseModel):
    ticker: str
    company_name: str
    exchange: str
    relevance_score: float


class CompanyInfoResponse(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    market_cap: float
    description: str


class FinancialMetricsResponse(BaseModel):
    ticker: str
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None


class StockDetailResponse(BaseModel):
    price: StockPriceResponse
    company: Optional[CompanyInfoResponse] = None
    metrics: Optional[FinancialMetricsResponse] = None


def get_stock_data_service() -> StockDataService:
    """Dependency to get StockDataService instance."""
    from app.mcp.factory import get_mcp_factory
    factory = get_mcp_factory()
    mcp_tools = StockDataMCPTools(factory.get_stock_data_client())
    return StockDataService(mcp_tools)


@router.get("/search", response_model=List[StockSearchResult])
@limiter.limit("60/minute")
async def search_stocks(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query (ticker or company name)"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="Maximum number of results"),
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Search for stocks by ticker symbol or company name.
    
    Rate limit: 60 requests per minute.
    
    Query parameters:
    - q: Search query (required)
    - limit: Maximum number of results (default: 10, max: 50)
    """
    try:
        # Validate and sanitize search query
        sanitized_query = validate_search_query(q)
        
        try:
            results = await stock_service.searchStocks(sanitized_query, limit)
            return [
                {
                    "ticker": r.ticker,
                    "company_name": r.company_name,
                    "exchange": r.exchange,
                    "relevance_score": r.relevance_score
                }
                for r in results
            ]
        except Exception as mcp_error:
            # Fallback to static list if MCP is unavailable
            logger.warning(f"MCP search failed, using fallback: {mcp_error}")
            
            # Common stocks for fallback
            common_stocks = [
                {"ticker": "AAPL", "company_name": "Apple Inc.", "exchange": "NASDAQ"},
                {"ticker": "MSFT", "company_name": "Microsoft Corporation", "exchange": "NASDAQ"},
                {"ticker": "GOOGL", "company_name": "Alphabet Inc.", "exchange": "NASDAQ"},
                {"ticker": "AMZN", "company_name": "Amazon.com Inc.", "exchange": "NASDAQ"},
                {"ticker": "TSLA", "company_name": "Tesla Inc.", "exchange": "NASDAQ"},
                {"ticker": "META", "company_name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
                {"ticker": "NVDA", "company_name": "NVIDIA Corporation", "exchange": "NASDAQ"},
                {"ticker": "JPM", "company_name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
                {"ticker": "V", "company_name": "Visa Inc.", "exchange": "NYSE"},
                {"ticker": "WMT", "company_name": "Walmart Inc.", "exchange": "NYSE"},
            ]
            
            # Filter by query
            query_upper = sanitized_query.upper()
            filtered = [
                {**stock, "relevance_score": 1.0 if stock["ticker"] == query_upper else 0.8}
                for stock in common_stocks
                if query_upper in stock["ticker"] or query_upper in stock["company_name"].upper()
            ]
            
            return filtered[:limit]
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search stocks: {str(e)}"
        )


class BatchPriceRequest(BaseModel):
    tickers: List[str]


@router.post("/prices/batch")
@limiter.limit("30/minute")
async def get_batch_prices(
    request: Request,
    body: BatchPriceRequest,
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """Get current prices for multiple tickers."""
    try:
        prices = await stock_service.getBatchPrices(body.tickers)
        return {
            ticker: {
                "ticker": p.ticker,
                "price": p.price,
                "change": p.change,
                "change_percent": p.change_percent,
                "volume": p.volume,
                "timestamp": p.timestamp.isoformat()
            }
            for ticker, p in prices.items()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch batch prices: {str(e)}"
        )


@router.get("/{ticker}", response_model=StockDetailResponse)
@limiter.limit("60/minute")
async def get_stock_details(
    request: Request,
    ticker: str,
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Get complete stock details including price, company info, and financial metrics.
    
    Rate limit: 60 requests per minute.
    """
    try:
        ticker = validate_ticker(ticker)
        
        # Fetch all data concurrently, tolerate partial failures
        price_result, company_result, metrics_result = await asyncio.gather(
            stock_service.getCurrentPrice(ticker),
            stock_service.getCompanyInfo(ticker),
            stock_service.getFinancialMetrics(ticker),
            return_exceptions=True
        )
        
        # Price is required — fail if unavailable
        if isinstance(price_result, Exception):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Stock price unavailable for {ticker}: {str(price_result)}"
            )
        
        price = price_result
        company = None if isinstance(company_result, Exception) else company_result
        metrics = None if isinstance(metrics_result, Exception) else metrics_result
        
        return {
            "price": {
                "ticker": price.ticker,
                "price": price.price,
                "change": price.change,
                "change_percent": price.change_percent,
                "volume": price.volume,
                "timestamp": price.timestamp.isoformat()
            },
            "company": {
                "ticker": company.ticker,
                "name": company.name,
                "sector": company.sector,
                "industry": company.industry,
                "market_cap": company.market_cap,
                "description": company.description
            } if company else None,
            "metrics": {
                "ticker": metrics.ticker,
                "pe_ratio": metrics.pe_ratio,
                "eps": metrics.eps,
                "dividend_yield": metrics.dividend_yield,
                "beta": metrics.beta,
                "fifty_two_week_high": metrics.fifty_two_week_high,
                "fifty_two_week_low": metrics.fifty_two_week_low
            } if metrics else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch stock details: {str(e)}"
        )


@router.get("/{ticker}/price", response_model=StockPriceResponse)
@limiter.limit("120/minute")
async def get_stock_price(
    request: Request,
    ticker: str,
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Get current stock price.
    
    Rate limit: 120 requests per minute.
    Cached for 60 seconds.
    """
    try:
        ticker = ticker.upper()
        price = await stock_service.getCurrentPrice(ticker)
        
        return {
            "ticker": price.ticker,
            "price": price.price,
            "change": price.change,
            "change_percent": price.change_percent,
            "volume": price.volume,
            "timestamp": price.timestamp.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stock price: {str(e)}"
        )


@router.get("/{ticker}/historical", response_model=List[HistoricalDataPoint])
@limiter.limit("30/minute")
async def get_historical_data(
    request: Request,
    ticker: str,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Get historical price data for a stock.
    
    Rate limit: 30 requests per minute.
    Cached for 1 hour.
    
    Query parameters:
    - start_date: Start date (required, format: YYYY-MM-DD)
    - end_date: End date (required, format: YYYY-MM-DD)
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date"
        )
    
    try:
        ticker = ticker.upper()
        data = await stock_service.getHistoricalData(ticker, start_date, end_date)
        
        return [
            {
                "date": point.date.isoformat(),
                "open": point.open,
                "high": point.high,
                "low": point.low,
                "close": point.close,
                "volume": point.volume
            }
            for point in data
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch historical data: {str(e)}"
        )


@router.get("/{ticker}/company", response_model=CompanyInfoResponse)
@limiter.limit("60/minute")
async def get_company_info(
    request: Request,
    ticker: str,
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Get company information for a stock.
    
    Rate limit: 60 requests per minute.
    Cached for 1 hour.
    """
    try:
        ticker = ticker.upper()
        company = await stock_service.getCompanyInfo(ticker)
        
        return {
            "ticker": company.ticker,
            "name": company.name,
            "sector": company.sector,
            "industry": company.industry,
            "market_cap": company.market_cap,
            "description": company.description
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch company info: {str(e)}"
        )


@router.get("/{ticker}/metrics", response_model=FinancialMetricsResponse)
@limiter.limit("60/minute")
async def get_financial_metrics(
    request: Request,
    ticker: str,
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Get financial metrics for a stock.
    
    Rate limit: 60 requests per minute.
    Cached for 1 hour.
    """
    try:
        ticker = ticker.upper()
        metrics = await stock_service.getFinancialMetrics(ticker)
        
        return {
            "ticker": metrics.ticker,
            "pe_ratio": metrics.pe_ratio,
            "eps": metrics.eps,
            "dividend_yield": metrics.dividend_yield,
            "beta": metrics.beta,
            "fifty_two_week_high": metrics.fifty_two_week_high,
            "fifty_two_week_low": metrics.fifty_two_week_low
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch financial metrics: {str(e)}"
        )
