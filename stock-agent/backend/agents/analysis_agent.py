from typing import Dict, Any
from services.openai_agent import OpenAIAgent
from .state import StockAnalysisState

class AnalysisAgent:
    def __init__(self):
        self.openai_agent = OpenAIAgent()
    
    async def analyze_sentiment(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            news_articles = state.get('news_articles', [])
            
            if not news_articles:
                print("AnalysisAgent: No news articles to analyze")
                return {
                    "sentiment_analyzed": True,
                    "next_action": "query_vector_store"
                }
            
            print(f"AnalysisAgent: Analyzing sentiment for {len(news_articles)} articles")
            analyzed_news = await self.openai_agent.analyze_news_sentiment(news_articles)
            
            return {
                "news_articles": analyzed_news,
                "sentiment_analyzed": True,
                "next_action": "query_vector_store"
            }
        except Exception as e:
            print(f"AnalysisAgent: Error analyzing sentiment: {e}")
            return {
                "sentiment_analyzed": False,
                "errors": [f"Sentiment analysis error: {str(e)}"],
                "next_action": "query_vector_store"
            }
