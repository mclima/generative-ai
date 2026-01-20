from fastapi import APIRouter, HTTPException, Request
from typing import List
from agents.workflow import StockAnalysisWorkflow
from models.stock_models import StockData, ChartData, NewsArticle, HistoricalData

router = APIRouter()

@router.get("/stock/{symbol}/analysis")
async def get_full_analysis(symbol: str, request: Request):
    try:
        print(f"\n=== Full analysis request for {symbol} ===")
        vector_service = request.app.state.vector_service
        workflow = StockAnalysisWorkflow(vector_service)
        
        result = await workflow.run(symbol)
        
        if result.get('errors'):
            print(f"Workflow completed with errors: {result['errors']}")
        
        return {
            "stock_data": result.get('stock_data'),
            "chart_data": result.get('chart_data'),
            "historical_data": result.get('historical_data'),
            "news": result.get('news_articles'),
            "insights": result.get('insights'),
            "errors": result.get('errors', [])
        }
    except Exception as e:
        print(f"Error in full analysis: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}", response_model=StockData)
async def get_stock_data(symbol: str, request: Request):
    try:
        print(f"Getting stock data for {symbol} (direct)")
        from services.polygon_service import PolygonService
        poly_service = PolygonService()
        data = await poly_service.get_stock_quote(symbol)
        return data
    except Exception as e:
        print(f"Error in get_stock_data: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/chart", response_model=List[ChartData])
async def get_chart_data(symbol: str, request: Request, timeframe: str = "1M"):
    try:
        from services.polygon_service import PolygonService
        poly_service = PolygonService()
        data = await poly_service.get_chart_data(symbol, timeframe)
        return data
    except Exception as e:
        print(f"Error in get_chart_data: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/historical", response_model=List[HistoricalData])
async def get_historical_data(symbol: str, request: Request, limit: int = 30):
    try:
        from services.polygon_service import PolygonService
        poly_service = PolygonService()
        data = await poly_service.get_historical_data(symbol, limit)
        return data
    except Exception as e:
        print(f"Error in get_historical_data: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/news", response_model=List[NewsArticle])
async def get_stock_news(symbol: str, request: Request):
    try:
        from services.polygon_service import PolygonService
        from services.openai_agent import OpenAIAgent
        
        poly_service = PolygonService()
        ai_agent = OpenAIAgent()
        
        news = await poly_service.get_stock_news(symbol, limit=6)
        
        vector_service = request.app.state.vector_service
        for article in news:
            await vector_service.add_news_article(symbol, article)
        
        analyzed_news = await ai_agent.analyze_news_sentiment(news)
        return analyzed_news
    except Exception as e:
        print(f"Error in get_stock_news: {type(e).__name__}: {str(e)}")
        if "Rate limit" in str(e):
            raise HTTPException(status_code=429, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/insights")
async def get_ai_insights(symbol: str, request: Request):
    try:
        print(f"Getting insights for {symbol} via LangGraph")
        vector_service = request.app.state.vector_service
        workflow = StockAnalysisWorkflow(vector_service)
        
        result = await workflow.run(symbol)
        
        if not result.get('insights'):
            errors = result.get('errors', [])
            error_msg = errors[0] if errors else "Insights not available"
            
            if "Rate limit" in error_msg:
                raise HTTPException(status_code=429, detail=error_msg)
            
            raise HTTPException(status_code=500, detail=error_msg)
        
        return result['insights']
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_ai_insights: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
