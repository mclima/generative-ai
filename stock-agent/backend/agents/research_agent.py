from typing import Dict, Any
from services.vector_store import VectorStoreService
from .state import StockAnalysisState

class ResearchAgent:
    def __init__(self, vector_service: VectorStoreService):
        self.vector_service = vector_service
    
    async def query_vector_store(self, state: StockAnalysisState) -> Dict[str, Any]:
        try:
            print(f"ResearchAgent: Querying vector store for {state['symbol']}")
            
            news_articles = state.get('news_articles', [])
            if news_articles:
                for article in news_articles:
                    await self.vector_service.add_news_article(state['symbol'], article)
            
            context = await self.vector_service.get_relevant_context(state['symbol'])
            
            return {
                "vector_context": context,
                "next_action": "generate_insights"
            }
        except Exception as e:
            print(f"ResearchAgent: Error querying vector store: {e}")
            return {
                "errors": [f"Vector store error: {str(e)}"],
                "next_action": "generate_insights"
            }
