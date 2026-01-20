from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StockData(BaseModel):
    symbol: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    pe_ratio: float
    high_52week: float
    low_52week: float

class ChartData(BaseModel):
    date: str
    price: float
    volume: int

class HistoricalData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    change_percent: float

class NewsArticle(BaseModel):
    title: str
    description: str
    url: str
    published_at: str
    source: str
    sentiment: Optional[str] = None

class AIInsight(BaseModel):
    type: str
    title: str
    description: str

class InsightsResponse(BaseModel):
    summary: str
    insights: List[AIInsight]
