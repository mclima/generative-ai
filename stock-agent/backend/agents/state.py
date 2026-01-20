from typing import TypedDict, List, Optional, Annotated
from operator import add

class StockAnalysisState(TypedDict):
    symbol: str
    stock_data: Optional[dict]
    chart_data: Optional[List[dict]]
    historical_data: Optional[List[dict]]
    news_articles: Optional[List[dict]]
    sentiment_analyzed: bool
    vector_context: Optional[str]
    insights: Optional[dict]
    errors: Annotated[List[str], add]
    next_action: str
