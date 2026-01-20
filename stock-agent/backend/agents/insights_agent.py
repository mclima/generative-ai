from typing import Dict, Any
from services.openai_agent import OpenAIAgent
from .state import StockAnalysisState

class InsightsAgent:
    def __init__(self):
        self.openai_agent = OpenAIAgent()
    
    async def generate_insights(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            print(f"InsightsAgent: Generating insights for {state['symbol']}")
            
            stock_data = state.get('stock_data')
            news_articles = state.get('news_articles', [])[:3]
            vector_context = state.get('vector_context', '')
            
            if not stock_data:
                return {
                    "errors": ["Cannot generate insights without stock data"],
                    "next_action": "end"
                }
            
            insights = await self.openai_agent.generate_insights(
                state['symbol'],
                stock_data,
                news_articles,
                vector_context
            )
            
            return {
                "insights": insights,
                "next_action": "end"
            }
        except Exception as e:
            print(f"InsightsAgent: Error generating insights: {e}")
            return {
                "errors": [f"Insights generation error: {str(e)}"],
                "next_action": "end"
            }
