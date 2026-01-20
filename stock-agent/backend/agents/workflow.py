from langgraph.graph import StateGraph, END
from services.vector_store import VectorStoreService
from .state import StockAnalysisState
from .manager_agent import ManagerAgent
from .data_agent import DataAgent
from .analysis_agent import AnalysisAgent
from .research_agent import ResearchAgent
from .insights_agent import InsightsAgent

class StockAnalysisWorkflow:
    def __init__(self, vector_service: VectorStoreService):
        self.manager = ManagerAgent()
        self.data_agent = DataAgent()
        self.analysis_agent = AnalysisAgent()
        self.research_agent = ResearchAgent(vector_service)
        self.insights_agent = InsightsAgent()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(StockAnalysisState)
        
        workflow.add_node("fetch_stock", self.data_agent.fetch_stock_data)
        workflow.add_node("fetch_chart", self.data_agent.fetch_chart_data)
        workflow.add_node("fetch_historical", self.data_agent.fetch_historical_data)
        workflow.add_node("fetch_news", self.data_agent.fetch_news)
        workflow.add_node("analyze_sentiment", self.analysis_agent.analyze_sentiment)
        workflow.add_node("query_vector_store", self.research_agent.query_vector_store)
        workflow.add_node("generate_insights", self.insights_agent.generate_insights)
        
        workflow.set_entry_point("fetch_stock")
        
        workflow.add_conditional_edges(
            "fetch_stock",
            self.manager.route_next_action,
            {
                "fetch_chart": "fetch_chart",
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "fetch_chart",
            self.manager.route_next_action,
            {
                "fetch_historical": "fetch_historical",
                "fetch_news": "fetch_news",
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "fetch_historical",
            self.manager.route_next_action,
            {
                "fetch_news": "fetch_news",
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "fetch_news",
            self.manager.route_next_action,
            {
                "analyze_sentiment": "analyze_sentiment",
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "analyze_sentiment",
            self.manager.route_next_action,
            {
                "query_vector_store": "query_vector_store",
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "query_vector_store",
            self.manager.route_next_action,
            {
                "generate_insights": "generate_insights",
                "end": END
            }
        )
        
        workflow.add_edge("generate_insights", END)
        
        return workflow.compile()
    
    async def run(self, symbol: str) -> StockAnalysisState:
        initial_state: StockAnalysisState = {
            "symbol": symbol,
            "stock_data": None,
            "chart_data": None,
            "historical_data": None,
            "news_articles": None,
            "sentiment_analyzed": False,
            "vector_context": None,
            "insights": None,
            "errors": [],
            "next_action": "fetch_stock"
        }
        
        print(f"\n=== Starting LangGraph workflow for {symbol} ===\n")
        result = await self.graph.ainvoke(initial_state)
        print(f"\n=== Workflow complete for {symbol} ===\n")
        
        return result
