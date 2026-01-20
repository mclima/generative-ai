import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.stock_models import StockData, ChartData, NewsArticle, HistoricalData

class PolygonService:
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 60  # Cache for 60 seconds
    
    async def get_stock_quote(self, symbol: str) -> StockData:
        try:
            # Check cache first
            cache_key = f"quote_{symbol}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_duration:
                    print(f"Returning cached data for {symbol}")
                    return cached_data
            
            # Use previous close endpoint (free tier compatible)
            prev_close_url = f"{self.base_url}/v2/aggs/ticker/{symbol}/prev"
            params = {"apiKey": self.api_key, "adjusted": "true"}
            
            print(f"Fetching stock data for {symbol}...")
            response = requests.get(prev_close_url, params=params)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds.")
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                print(f"Error response: {error_data}")
                error_msg = error_data.get('error', error_data.get('message', response.text))
                if 'exceeded the maximum requests' in str(error_msg):
                    raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds.")
                raise Exception(f"Polygon API error: {error_msg}")
            
            data = response.json()
            print(f"Response data: {data}")
            
            if "results" not in data or not data["results"]:
                raise Exception(f"No data found for {symbol}. Please use US stock symbols (e.g., AAPL, TSLA, GOOGL). Futures and options are not supported on the free tier.")
            
            result = data["results"][0]
            current_price = result.get("c", 0)
            open_price = result.get("o", current_price)
            change = current_price - open_price
            change_percent = (change / open_price * 100) if open_price else 0
            
            # Get 52-week range from aggregates
            year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            aggregates_url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{year_ago}/{today}"
            agg_response = requests.get(aggregates_url, params=params)
            agg_data = agg_response.json() if agg_response.ok else {}
            
            results = agg_data.get("results", [])
            high_52week = max([r.get("h", 0) for r in results]) if results else current_price
            low_52week = min([r.get("l", current_price) for r in results]) if results else current_price
            
            stock_data = StockData(
                symbol=symbol,
                current_price=current_price,
                change=change,
                change_percent=change_percent,
                volume=result.get("v", 0),
                market_cap=1000000000,  # Default value as free tier doesn't provide this
                pe_ratio=15.5,  # Default value
                high_52week=high_52week,
                low_52week=low_52week
            )
            
            # Cache the result
            self.cache[cache_key] = (stock_data, datetime.now())
            return stock_data
        except Exception as e:
            raise Exception(f"Error fetching stock data: {str(e)}")
    
    async def get_chart_data(self, symbol: str, timeframe: str = "1M") -> List[ChartData]:
        try:
            days_map = {"1D": 1, "1W": 7, "1M": 30, "3M": 90, "1Y": 365}
            days = days_map.get(timeframe, 30)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {"apiKey": self.api_key, "adjusted": "true", "sort": "asc"}
            
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds before searching again.")
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', error_data.get('message', response.text))
                if 'exceeded the maximum requests' in str(error_msg):
                    raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds before searching again.")
                raise Exception(f"Polygon API error: {error_msg}")
            
            data = response.json()
            
            results = data.get("results", [])
            chart_data = []
            
            for item in results:
                chart_data.append(ChartData(
                    date=datetime.fromtimestamp(item["t"] / 1000).strftime("%Y-%m-%d"),
                    price=item["c"],
                    volume=item["v"]
                ))
            
            return chart_data
        except Exception as e:
            raise Exception(f"Error fetching chart data: {str(e)}")
    
    async def get_historical_data(self, symbol: str, limit: int = 30) -> List[HistoricalData]:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=limit + 10)
            
            url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/day/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            params = {"apiKey": self.api_key, "adjusted": "true", "sort": "desc", "limit": limit}
            
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds before searching again.")
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', error_data.get('message', response.text))
                if 'exceeded the maximum requests' in str(error_msg):
                    raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds before searching again.")
                raise Exception(f"Polygon API error: {error_msg}")
            
            data = response.json()
            
            results = data.get("results", [])[:limit]
            historical_data = []
            
            for i, item in enumerate(results):
                prev_close = results[i + 1]["c"] if i + 1 < len(results) else item["o"]
                change_percent = ((item["c"] - prev_close) / prev_close * 100) if prev_close else 0
                
                historical_data.append(HistoricalData(
                    date=datetime.fromtimestamp(item["t"] / 1000).strftime("%Y-%m-%d"),
                    open=item["o"],
                    high=item["h"],
                    low=item["l"],
                    close=item["c"],
                    volume=item["v"],
                    change_percent=change_percent
                ))
            
            return historical_data
        except Exception as e:
            raise Exception(f"Error fetching historical data: {str(e)}")
    
    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[NewsArticle]:
        try:
            url = f"{self.base_url}/v2/reference/news"
            params = {
                "apiKey": self.api_key,
                "ticker": symbol,
                "limit": limit,
                "sort": "published_utc",
                "order": "desc"
            }
            
            print(f"Fetching news from Polygon API for {symbol}")
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds before searching again.")
            
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                print(f"News API error response: {error_data}")
                error_msg = error_data.get('error', error_data.get('message', response.text))
                if 'exceeded the maximum requests' in str(error_msg):
                    raise Exception("Rate limit exceeded. Free tier allows 5 calls/minute. Please wait 60 seconds before searching again.")
                raise Exception(f"Polygon API error: {error_msg}")
            
            data = response.json()
            print(f"News API response: {data.get('count', 0)} articles found")
            
            news_articles = []
            for item in data.get("results", []):
                news_articles.append(NewsArticle(
                    title=item.get("title", ""),
                    description=item.get("description", "")[:200] if item.get("description") else "",
                    url=item.get("article_url", ""),
                    published_at=item.get("published_utc", ""),
                    source=item.get("publisher", {}).get("name", "Unknown") if item.get("publisher") else "Unknown"
                ))
            
            print(f"Parsed {len(news_articles)} news articles")
            return news_articles
        except Exception as e:
            print(f"Error in get_stock_news: {str(e)}")
            raise Exception(f"Error fetching news: {str(e)}")
