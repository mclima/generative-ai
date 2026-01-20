from typing import Dict, Any
from services.polygon_service import PolygonService
from .state import StockAnalysisState

class DataAgent:
    def __init__(self):
        self.polygon_service = PolygonService()
    
    async def fetch_stock_data(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            print(f"DataAgent: Fetching stock data for {state['symbol']}")
            stock_data = await self.polygon_service.get_stock_quote(state['symbol'])
            return {
                "stock_data": stock_data,
                "next_action": "fetch_chart"
            }
        except Exception as e:
            print(f"DataAgent: Error fetching stock data: {e}")
            return {
                "errors": [f"Stock data error: {str(e)}"],
                "next_action": "error"
            }
    
    async def fetch_chart_data(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            print(f"DataAgent: Fetching chart data for {state['symbol']}")
            chart_data = await self.polygon_service.get_chart_data(state['symbol'], "1M")
            return {
                "chart_data": chart_data,
                "next_action": "fetch_historical"
            }
        except Exception as e:
            print(f"DataAgent: Error fetching chart data: {e}")
            return {
                "errors": [f"Chart data error: {str(e)}"],
                "next_action": "fetch_historical"
            }
    
    async def fetch_historical_data(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            print(f"DataAgent: Fetching historical data for {state['symbol']}")
            historical_data = await self.polygon_service.get_historical_data(state['symbol'], limit=30)
            return {
                "historical_data": historical_data,
                "next_action": "fetch_news"
            }
        except Exception as e:
            print(f"DataAgent: Error fetching historical data: {e}")
            return {
                "errors": [f"Historical data error: {str(e)}"],
                "next_action": "fetch_news"
            }
    
    async def fetch_news(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            print(f"DataAgent: Fetching news for {state['symbol']}")
            news_articles = await self.polygon_service.get_stock_news(state['symbol'], limit=6)
            return {
                "news_articles": news_articles,
                "next_action": "analyze_sentiment"
            }
        except Exception as e:
            print(f"DataAgent: Error fetching news: {e}")
            return {
                "errors": [f"News data error: {str(e)}"],
                "next_action": "generate_insights"
            }
