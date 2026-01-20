from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from datetime import datetime, timedelta

from services.polygon_service import PolygonService
from services.openai_agent import OpenAIAgent
from services.vector_store import VectorStoreService
from models.stock_models import StockData, ChartData, NewsArticle, AIInsight, HistoricalData

router = APIRouter()
polygon_service = None
openai_agent = None

def get_services():
    global polygon_service, openai_agent
    if polygon_service is None:
        polygon_service = PolygonService()
    if openai_agent is None:
        openai_agent = OpenAIAgent()
    return polygon_service, openai_agent

@router.get("/stock/{symbol}", response_model=StockData)
async def get_stock_data(symbol: str):
    try:
        print(f"Getting stock data for {symbol}")
        poly_service, _ = get_services()
        print(f"Services initialized: {poly_service is not None}")
        data = await poly_service.get_stock_quote(symbol)
        print(f"Data retrieved successfully")
        return data
    except Exception as e:
        print(f"Error in get_stock_data: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/chart", response_model=List[ChartData])
async def get_chart_data(symbol: str, timeframe: str = "1M"):
    try:
        poly_service, _ = get_services()
        data = await poly_service.get_chart_data(symbol, timeframe)
        return data
    except Exception as e:
        print(f"Error in get_chart_data: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/historical", response_model=List[HistoricalData])
async def get_historical_data(symbol: str, limit: int = 30):
    try:
        print(f"Fetching historical data for {symbol}")
        poly_service, _ = get_services()
        data = await poly_service.get_historical_data(symbol, limit)
        print(f"Historical data retrieved: {len(data)} records")
        return data
    except Exception as e:
        print(f"Error in get_historical_data: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/news", response_model=List[NewsArticle])
async def get_stock_news(symbol: str, request: Request):
    try:
        print(f"Fetching news for {symbol}")
        poly_service, ai_agent = get_services()
        news = await poly_service.get_stock_news(symbol, limit=6)
        print(f"News retrieved: {len(news)} articles")
        
        vector_service = request.app.state.vector_service
        for article in news:
            await vector_service.add_news_article(symbol, article)
        
        print(f"Analyzing sentiment for {len(news)} articles")
        analyzed_news = await ai_agent.analyze_news_sentiment(news)
        print(f"Sentiment analysis complete")
        return analyzed_news
    except Exception as e:
        print(f"Error in get_stock_news: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/insights")
async def get_ai_insights(symbol: str, request: Request):
    try:
        poly_service, ai_agent = get_services()
        stock_data = await poly_service.get_stock_quote(symbol)
        
        # Get news from vector store (already cached from news endpoint)
        # This avoids hitting rate limits by not fetching news again
        vector_service = request.app.state.vector_service
        context = await vector_service.get_relevant_context(symbol)
        
        # Use empty news list since context already contains news info
        # Or fetch minimal news only if absolutely needed
        news = []
        
        insights = await ai_agent.generate_insights(symbol, stock_data, news, context)
        return insights
    except Exception as e:
        print(f"Error in get_ai_insights: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
