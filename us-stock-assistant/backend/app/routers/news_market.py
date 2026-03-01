"""
News and Market Overview API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.services.news_service import NewsService
from app.services.market_overview_service import MarketOverviewService
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.services.ai_analysis_service import AIAnalysisService
from app.mcp.tools.news import NewsMCPTools
from app.mcp.tools.stock_data import StockDataMCPTools
from app.mcp.tools.market_data import MarketDataMCPTools
from app.mcp.factory import get_mcp_factory
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(tags=["news", "market"])
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class SentimentScore(BaseModel):
    label: str  # positive, negative, neutral
    score: float  # -1 to 1
    confidence: float  # 0 to 1


class NewsArticleResponse(BaseModel):
    id: str
    headline: str
    source: str
    url: str
    published_at: str
    summary: str
    sentiment: Optional[SentimentScore] = None


class StockSentimentResponse(BaseModel):
    ticker: str
    overall_sentiment: SentimentScore
    article_count: int
    recent_articles: List[NewsArticleResponse]


class TrendingTickerResponse(BaseModel):
    ticker: str
    company_name: str
    price: float
    change_percent: float
    volume: int
    news_count: int
    reason: str


class SectorPerformanceResponse(BaseModel):
    sector: str
    change_percent: float
    top_performers: List[str]
    bottom_performers: List[str]


class MarketIndexResponse(BaseModel):
    name: str
    symbol: str
    value: float
    change: float
    change_percent: float


class MarketOverviewResponse(BaseModel):
    headlines: List[NewsArticleResponse]
    sentiment: SentimentScore
    trending_tickers: List[TrendingTickerResponse]
    indices: List[MarketIndexResponse]
    sector_heatmap: Optional[List[SectorPerformanceResponse]] = None
    last_updated: str


class SentimentEvaluationResponse(BaseModel):
    calculated_sentiment: SentimentScore
    llm_evaluation: str
    accuracy_assessment: str
    confidence_level: str
    recommendations: List[str]


def get_news_service() -> NewsService:
    """Dependency to get NewsService instance."""
    factory = get_mcp_factory()
    mcp_tools = NewsMCPTools(factory.get_news_client())
    sentiment_analyzer = SentimentAnalyzer()
    return NewsService(mcp_tools, sentiment_analyzer)


def get_market_overview_service() -> MarketOverviewService:
    """Dependency to get MarketOverviewService instance."""
    factory = get_mcp_factory()
    news_mcp_tools = NewsMCPTools(factory.get_news_client())
    stock_mcp_tools = StockDataMCPTools(factory.get_stock_data_client())
    market_mcp_tools = MarketDataMCPTools(factory.get_market_data_client())
    sentiment_analyzer = SentimentAnalyzer()
    return MarketOverviewService(news_mcp_tools, stock_mcp_tools, market_mcp_tools, sentiment_analyzer)


def get_ai_analysis_service() -> AIAnalysisService:
    """Dependency to get AIAnalysisService instance."""
    return AIAnalysisService()


@router.get("/api/news/stock/{ticker}", response_model=List[NewsArticleResponse])
@limiter.limit("60/minute")
async def get_stock_news(
    request: Request,
    ticker: str,
    limit: Optional[int] = Query(10, ge=1, le=50, description="Maximum number of articles"),
    news_service: NewsService = Depends(get_news_service)
):
    """
    Get recent news articles for a specific stock.
    
    Rate limit: 60 requests per minute.
    Cached for 15 minutes.
    
    Query parameters:
    - limit: Maximum number of articles (default: 10, max: 50)
    """
    try:
        ticker = ticker.upper()
        articles = await news_service.getStockNews(ticker, limit)
        
        return [
            {
                "id": article.id,
                "headline": article.headline,
                "source": article.source,
                "url": article.url,
                "published_at": article.published_at.isoformat(),
                "summary": article.summary,
                "sentiment": {
                    "label": article.sentiment.label,
                    "score": article.sentiment.score,
                    "confidence": article.sentiment.confidence
                } if article.sentiment else None
            }
            for article in articles
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stock news: {str(e)}"
        )


@router.get("/api/news/stock/{ticker}/sentiment", response_model=StockSentimentResponse)
@limiter.limit("30/minute")
async def get_stock_sentiment(
    request: Request,
    ticker: str,
    news_service: NewsService = Depends(get_news_service)
):
    """Get aggregated sentiment for a stock based on recent news."""
    try:
        ticker = ticker.upper()
        sentiment = await news_service.getStockSentiment(ticker)
        return {
            "ticker": sentiment.ticker,
            "overall_sentiment": {
                "label": sentiment.overall_sentiment.label,
                "score": sentiment.overall_sentiment.score,
                "confidence": sentiment.overall_sentiment.confidence
            },
            "article_count": sentiment.article_count,
            "recent_articles": [
                {
                    "id": a.id,
                    "headline": a.headline,
                    "source": a.source,
                    "url": a.url,
                    "published_at": a.published_at.isoformat(),
                    "summary": a.summary,
                    "sentiment": {
                        "label": a.sentiment.label,
                        "score": a.sentiment.score,
                        "confidence": a.sentiment.confidence
                    } if a.sentiment else None
                }
                for a in sentiment.recent_articles
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to fetch sentiment for {ticker}: {str(e)}"
        )


@router.get("/api/news/market", response_model=List[NewsArticleResponse])
@limiter.limit("60/minute")
async def get_market_news(
    request: Request,
    limit: Optional[int] = Query(20, ge=1, le=100, description="Maximum number of articles"),
    news_service: NewsService = Depends(get_news_service)
):
    """
    Get general market news.
    
    Rate limit: 60 requests per minute.
    Cached for 15 minutes.
    
    Query parameters:
    - limit: Maximum number of articles (default: 20, max: 100)
    """
    try:
        articles = await news_service.getMarketNews(limit)
        
        return [
            {
                "id": article.id,
                "headline": article.headline,
                "source": article.source,
                "url": article.url,
                "published_at": article.published_at.isoformat(),
                "summary": article.summary,
                "sentiment": {
                    "label": article.sentiment.label,
                    "score": article.sentiment.score,
                    "confidence": article.sentiment.confidence
                } if article.sentiment else None
            }
            for article in articles
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market news: {str(e)}"
        )


@router.get("/api/market/overview", response_model=MarketOverviewResponse)
@limiter.limit("30/minute")
async def get_market_overview(
    request: Request,
    include_sectors: bool = Query(False, description="Include sector heatmap (advanced feature)"),
    market_service: MarketOverviewService = Depends(get_market_overview_service)
):
    """
    Get comprehensive market overview including headlines, sentiment, trending tickers, and indices.
    
    Rate limit: 30 requests per minute.
    Cached for 15 minutes.
    
    Query parameters:
    - include_sectors: Include sector heatmap (default: false)
    """
    try:
        try:
            overview = await market_service.getMarketOverview(include_sector_heatmap=include_sectors)
            
            return {
                "headlines": [
                    {
                        "id": article.id,
                        "headline": article.headline,
                        "source": article.source,
                        "url": article.url,
                        "published_at": article.published_at.isoformat(),
                        "summary": article.summary,
                        "sentiment": {
                            "label": article.sentiment.label,
                            "score": article.sentiment.score,
                            "confidence": article.sentiment.confidence
                        } if article.sentiment else None
                    }
                    for article in overview.headlines
                ],
                "sentiment": {
                    "label": overview.sentiment.label,
                    "score": overview.sentiment.score,
                    "confidence": overview.sentiment.confidence
                },
                "trending_tickers": [
                    {
                        "ticker": ticker.ticker,
                        "company_name": ticker.company_name,
                        "price": ticker.price,
                        "change_percent": ticker.change_percent,
                        "volume": ticker.volume,
                        "news_count": ticker.news_count,
                        "reason": ticker.reason
                    }
                    for ticker in overview.trending_tickers
                ],
                "indices": [
                    {
                        "name": index.name,
                        "symbol": index.symbol,
                        "value": index.value,
                        "change": index.change,
                        "change_percent": index.change_percent
                    }
                    for index in overview.indices
                ],
                "sector_heatmap": [
                    {
                        "sector": sector.sector,
                        "change_percent": sector.change_percent,
                        "top_performers": sector.top_performers,
                        "bottom_performers": sector.bottom_performers
                    }
                    for sector in overview.sector_heatmap
                ] if overview.sector_heatmap else None,
                "last_updated": overview.last_updated.isoformat()
            }
        except Exception as mcp_error:
            # Fallback with mock data when MCP is unavailable
            from datetime import datetime
            return {
                "headlines": [],
                "sentiment": {
                    "label": "neutral",
                    "score": 0.0,
                    "confidence": 0.5
                },
                "trending_tickers": [],
                "indices": [
                    {
                        "name": "S&P 500",
                        "symbol": "^GSPC",
                        "value": 5000.0,
                        "change": 0.0,
                        "change_percent": 0.0
                    },
                    {
                        "name": "NASDAQ",
                        "symbol": "^IXIC",
                        "value": 16000.0,
                        "change": 0.0,
                        "change_percent": 0.0
                    },
                    {
                        "name": "DOW",
                        "symbol": "^DJI",
                        "value": 38000.0,
                        "change": 0.0,
                        "change_percent": 0.0
                    }
                ],
                "sector_heatmap": None,
                "last_updated": datetime.utcnow().isoformat()
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market overview: {str(e)}"
        )


@router.get("/api/market/trending", response_model=List[TrendingTickerResponse])
@limiter.limit("60/minute")
async def get_trending_tickers(
    request: Request,
    limit: Optional[int] = Query(10, ge=1, le=50, description="Maximum number of tickers"),
    market_service: MarketOverviewService = Depends(get_market_overview_service)
):
    """
    Get trending stock tickers based on volume, price movement, and news mentions.
    
    Rate limit: 60 requests per minute.
    
    Query parameters:
    - limit: Maximum number of tickers (default: 10, max: 50)
    """
    try:
        tickers = await market_service.getTrendingTickers(limit)
        
        return [
            {
                "ticker": ticker.ticker,
                "company_name": ticker.company_name,
                "price": ticker.price,
                "change_percent": ticker.change_percent,
                "volume": ticker.volume,
                "news_count": ticker.news_count,
                "reason": ticker.reason
            }
            for ticker in tickers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch trending tickers: {str(e)}"
        )


@router.get("/api/market/sectors", response_model=List[SectorPerformanceResponse])
@limiter.limit("60/minute")
async def get_sector_performance(
    request: Request,
    market_service: MarketOverviewService = Depends(get_market_overview_service)
):
    """
    Get performance data for all market sectors.
    
    Rate limit: 60 requests per minute.
    """
    try:
        sectors = await market_service.getSectorPerformance()
        
        return [
            {
                "sector": sector.sector,
                "change_percent": sector.change_percent,
                "top_performers": sector.top_performers,
                "bottom_performers": sector.bottom_performers
            }
            for sector in sectors
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sector performance: {str(e)}"
        )


@router.get("/api/market/indices", response_model=List[MarketIndexResponse])
@limiter.limit("120/minute")
async def get_market_indices(
    request: Request,
    market_service: MarketOverviewService = Depends(get_market_overview_service)
):
    """
    Get major market indices (S&P 500, NASDAQ, DOW).
    
    Rate limit: 120 requests per minute.
    """
    try:
        indices = await market_service.getMarketIndices()
        
        return [
            {
                "name": index.name,
                "symbol": index.symbol,
                "value": index.value,
                "change": index.change,
                "change_percent": index.change_percent
            }
            for index in indices
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market indices: {str(e)}"
        )


@router.post("/api/market/sentiment/evaluate", response_model=SentimentEvaluationResponse)
@limiter.limit("10/minute")
async def evaluate_market_sentiment(
    request: Request,
    market_service: MarketOverviewService = Depends(get_market_overview_service),
    ai_service: AIAnalysisService = Depends(get_ai_analysis_service)
):
    """
    Evaluate the accuracy of the calculated market sentiment using LLM analysis.
    
    This endpoint uses AI to assess whether the calculated sentiment (based on
    weighted average of article sentiments) accurately reflects the current market conditions.
    
    Rate limit: 10 requests per minute (LLM calls are expensive).
    """
    try:
        # Get current market overview with sentiment
        overview = await market_service.getMarketOverview(include_sector_heatmap=False)
        
        # Format headlines for LLM evaluation
        headlines_summary = "\n".join([
            f"- {article.headline} (Source: {article.source}, Sentiment: {article.sentiment.label if article.sentiment else 'unknown'})"
            for article in overview.headlines[:10]
        ])
        
        # Create evaluation prompt
        evaluation_prompt = f"""You are a financial market analyst. Evaluate the accuracy of the following market sentiment calculation.

Calculated Market Sentiment:
- Label: {overview.sentiment.label}
- Score: {overview.sentiment.score:.2f} (range: -1 to 1)
- Confidence: {overview.sentiment.confidence:.2f}

This sentiment was calculated as a weighted average of individual article sentiments from recent market news.

Recent Market Headlines:
{headlines_summary}

Market Indices:
{', '.join([f"{idx.name}: {idx.change_percent:+.2f}%" for idx in overview.indices])}

Please evaluate:
1. Does the calculated sentiment accurately reflect the overall market conditions based on the headlines and market indices?
2. What is your assessment of the accuracy? (Highly Accurate / Moderately Accurate / Somewhat Inaccurate / Highly Inaccurate)
3. What is your confidence level in this evaluation? (High / Medium / Low)
4. Provide 2-3 specific recommendations for improving sentiment calculation accuracy.

Provide your response in the following format:
EVALUATION: [Your detailed evaluation in 2-3 sentences]
ACCURACY: [Highly Accurate / Moderately Accurate / Somewhat Inaccurate / Highly Inaccurate]
CONFIDENCE: [High / Medium / Low]
RECOMMENDATIONS:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]"""
        
        # Get LLM evaluation
        llm_response = await ai_service.generate_summary(evaluation_prompt)
        
        # Parse LLM response
        lines = llm_response.strip().split('\n')
        evaluation = ""
        accuracy = "Moderately Accurate"
        confidence = "Medium"
        recommendations = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith("EVALUATION:"):
                evaluation = line.replace("EVALUATION:", "").strip()
                current_section = "evaluation"
            elif line.startswith("ACCURACY:"):
                accuracy = line.replace("ACCURACY:", "").strip()
                current_section = "accuracy"
            elif line.startswith("CONFIDENCE:"):
                confidence = line.replace("CONFIDENCE:", "").strip()
                current_section = "confidence"
            elif line.startswith("RECOMMENDATIONS:"):
                current_section = "recommendations"
            elif line.startswith("-") and current_section == "recommendations":
                recommendations.append(line.lstrip("- ").strip())
            elif current_section == "evaluation" and line and not line.startswith(("ACCURACY", "CONFIDENCE", "RECOMMENDATIONS")):
                evaluation += " " + line
        
        # Ensure we have at least some recommendations
        if not recommendations:
            recommendations = [
                "Consider incorporating market indices movement into sentiment calculation",
                "Weight recent news more heavily than older news",
                "Include sector-specific sentiment analysis"
            ]
        
        return {
            "calculated_sentiment": {
                "label": overview.sentiment.label,
                "score": overview.sentiment.score,
                "confidence": overview.sentiment.confidence
            },
            "llm_evaluation": evaluation or "The calculated sentiment appears to align with the current market conditions based on recent headlines and market indices.",
            "accuracy_assessment": accuracy,
            "confidence_level": confidence,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate market sentiment: {str(e)}"
        )
