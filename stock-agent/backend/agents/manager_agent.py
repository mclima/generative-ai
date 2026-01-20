from typing import Dict, Any, Literal
from .state import StockAnalysisState

class ManagerAgent:
    """
    Supervisor/Manager agent that coordinates the workflow and decides next actions
    """
    
    def route_next_action(self, state: StockAnalysisState) -> Literal[
        "fetch_stock", "fetch_chart", "fetch_historical", "fetch_news",
        "analyze_sentiment", "query_vector_store", "generate_insights", "end"
    ]:
        next_action = state.get('next_action', 'fetch_stock')
        
        print(f"ManagerAgent: Routing to '{next_action}'")
        
        if next_action == "error":
            print(f"ManagerAgent: Error encountered, checking if we can continue...")
            if state.get('stock_data'):
                print(f"ManagerAgent: Have stock data, attempting to generate insights with available data")
                return "generate_insights"
            print(f"ManagerAgent: No stock data available, ending workflow")
            return "end"
        
        return next_action
    
    def should_continue(self, state: StockAnalysisState) -> Literal["continue", "end"]:
        next_action = state.get('next_action', 'end')
        
        if next_action == "end":
            print("ManagerAgent: Workflow complete")
            return "end"
        
        print(f"ManagerAgent: Continuing workflow")
        return "continue"
