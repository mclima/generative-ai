"""
AI Analysis API endpoints.
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

from app.services.ai_analysis_service import (
    AIAnalysisService,
    AnalysisContext,
    HistoricalDataPoint,
    NewsArticle as AINewsArticle,
    FinancialMetrics,
    MarketConditions
)
from app.services.stock_data_service import StockDataService
from app.services.news_service import NewsService
from app.services.portfolio_service import PortfolioService
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.mcp.tools.stock_data import StockDataMCPTools
from app.mcp.tools.news import NewsMCPTools
from app.database import get_db
from app.dependencies import CurrentUser
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class PriceAnalysisResponse(BaseModel):
    trend: Optional[str] = "neutral"
    support: Optional[float] = None
    resistance: Optional[float] = None
    volatility: Optional[str] = "medium"


class SentimentAnalysisResponse(BaseModel):
    overall: Optional[str] = "neutral"
    score: Optional[float] = 0.0
    news_count: int = 0


class StockAnalysisResponse(BaseModel):
    ticker: str
    summary: str
    price_analysis: PriceAnalysisResponse
    sentiment_analysis: SentimentAnalysisResponse
    recommendations: List[str]
    risks: List[str]
    generated_at: str


class RebalancingSuggestionResponse(BaseModel):
    action: str  # buy, sell, hold
    ticker: str
    reason: str
    suggested_amount: Optional[float] = 0.0

    @field_validator("suggested_amount", mode="before")
    @classmethod
    def coerce_none_to_zero(cls, v):
        return v if v is not None else 0.0


class PortfolioAnalysisResponse(BaseModel):
    overall_health: str  # good, fair, poor
    diversification_score: float
    risk_level: str  # high, medium, low
    rebalancing_suggestions: List[RebalancingSuggestionResponse]
    underperforming_stocks: List[str]
    opportunities: List[str]


def get_ai_analysis_service() -> AIAnalysisService:
    """Dependency to get AIAnalysisService instance."""
    return AIAnalysisService()


def get_stock_data_service() -> StockDataService:
    """Dependency to get StockDataService instance."""
    from app.mcp.factory import get_mcp_factory
    factory = get_mcp_factory()
    mcp_tools = StockDataMCPTools(factory.get_stock_data_client())
    return StockDataService(mcp_tools)


def get_news_service() -> NewsService:
    """Dependency to get NewsService instance."""
    from app.mcp.factory import get_mcp_factory
    factory = get_mcp_factory()
    mcp_tools = NewsMCPTools(factory.get_news_client())
    sentiment_analyzer = SentimentAnalyzer()
    return NewsService(mcp_tools, sentiment_analyzer)


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    """Dependency to get PortfolioService instance."""
    return PortfolioService(db)


@router.post("/stock/{ticker}", response_model=StockAnalysisResponse)
@limiter.limit("10/minute")
async def analyze_stock(
    request: Request,
    ticker: str,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service),
    stock_service: StockDataService = Depends(get_stock_data_service),
    news_service: NewsService = Depends(get_news_service)
):
    """
    Generate AI-powered analysis for a stock.
    
    Rate limit: 10 requests per minute (AI analysis is resource-intensive).
    Analysis timeout: 10 seconds.
    
    Returns comprehensive analysis including:
    - Price trends and volatility assessment
    - Market sentiment based on recent news
    - Investment recommendations
    - Risk factors
    """
    try:
        ticker = ticker.upper()
        
        # Gather context data
        from datetime import date, timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        # Fetch data concurrently, historical is non-fatal
        results = await asyncio.gather(
            stock_service.getHistoricalData(ticker, start_date, end_date),
            news_service.getStockNews(ticker, limit=10),
            stock_service.getFinancialMetrics(ticker),
            return_exceptions=True
        )
        historical_data = [] if isinstance(results[0], Exception) else results[0]
        news_articles = [] if isinstance(results[1], Exception) else results[1]
        financial_metrics = None if isinstance(results[2], Exception) else results[2]
        
        # Convert to AI service format
        ai_historical = [
            HistoricalDataPoint(
                date=point.date,
                open=point.open,
                high=point.high,
                low=point.low,
                close=point.close,
                volume=point.volume
            )
            for point in historical_data
        ]
        
        ai_news = [
            AINewsArticle(
                headline=article.headline,
                source=article.source,
                published_at=article.published_at,
                summary=article.summary,
                sentiment_label=article.sentiment.label if article.sentiment else None,
                sentiment_score=article.sentiment.score if article.sentiment else None,
            )
            for article in news_articles
        ]
        
        ai_metrics = FinancialMetrics(
            ticker=financial_metrics.ticker if financial_metrics else ticker,
            pe_ratio=financial_metrics.pe_ratio if financial_metrics else None,
            eps=financial_metrics.eps if financial_metrics else None,
            dividend_yield=financial_metrics.dividend_yield if financial_metrics else None,
            beta=financial_metrics.beta if financial_metrics else None,
            fifty_two_week_high=financial_metrics.fifty_two_week_high if financial_metrics else None,
            fifty_two_week_low=financial_metrics.fifty_two_week_low if financial_metrics else None
        )
        
        # Create analysis context
        context = AnalysisContext(
            historical_data=ai_historical,
            news=ai_news,
            financial_metrics=ai_metrics,
            market_conditions=None  # Optional
        )
        
        # Generate analysis
        analysis = await ai_service.analyzeStock(ticker, context)
        
        return {
            "ticker": analysis.ticker,
            "summary": analysis.summary,
            "price_analysis": {
                "trend": analysis.price_analysis.trend,
                "support": analysis.price_analysis.support,
                "resistance": analysis.price_analysis.resistance,
                "volatility": analysis.price_analysis.volatility
            },
            "sentiment_analysis": {
                "overall": analysis.sentiment_analysis.overall,
                "score": analysis.sentiment_analysis.score,
                "news_count": analysis.sentiment_analysis.news_count
            },
            "recommendations": analysis.recommendations,
            "risks": analysis.risks,
            "generated_at": analysis.generated_at.isoformat()
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Analysis request timed out. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate stock analysis: {str(e)}"
        )


@router.post("/portfolio", response_model=PortfolioAnalysisResponse)
@limiter.limit("5/minute")
async def analyze_portfolio(
    request: Request,
    current_user: CurrentUser,
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    stock_service: StockDataService = Depends(get_stock_data_service)
):
    """
    Generate AI-powered analysis for user's portfolio.
    
    Requires authentication.
    Rate limit: 5 requests per minute (AI analysis is resource-intensive).
    
    Returns comprehensive portfolio analysis including:
    - Overall health assessment
    - Diversification score
    - Risk level evaluation
    - Rebalancing suggestions
    - Underperforming stocks
    - Investment opportunities
    """
    try:
        # Get portfolio
        portfolio = portfolio_service.get_portfolio(current_user.id)
        
        if not portfolio or not portfolio.positions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio is empty. Add positions before requesting analysis."
            )
        
        # Get portfolio metrics
        metrics = await portfolio_service.calculate_metrics(current_user.id)
        
        # Get current prices for all positions
        tickers = [pos.ticker for pos in portfolio.positions]
        prices = await stock_service.getBatchPrices(tickers)
        
        # Format portfolio data
        positions = []
        for pos in portfolio.positions:
            current_price = prices.get(pos.ticker)
            if current_price:
                positions.append({
                    "ticker": pos.ticker,
                    "quantity": float(pos.quantity),
                    "purchase_price": float(pos.purchase_price),
                    "current_price": current_price.price,
                    "current_value": float(pos.quantity) * current_price.price,
                    "gain_loss": (current_price.price - float(pos.purchase_price)) * float(pos.quantity),
                    "gain_loss_percent": ((current_price.price - float(pos.purchase_price)) / float(pos.purchase_price)) * 100
                })
        
        # Generate analysis
        analysis = await ai_service.analyzePortfolio(positions, metrics)
        
        return {
            "overall_health": analysis.overall_health,
            "diversification_score": analysis.diversification_score,
            "risk_level": analysis.risk_level,
            "rebalancing_suggestions": [
                {
                    "action": suggestion.action,
                    "ticker": suggestion.ticker,
                    "reason": suggestion.reason,
                    "suggested_amount": suggestion.suggested_amount or 0.0
                }
                for suggestion in analysis.rebalancing_suggestions
            ],
            "underperforming_stocks": analysis.underperforming_stocks,
            "opportunities": analysis.opportunities
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Analysis request timed out. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate portfolio analysis: {str(e)}"
        )
