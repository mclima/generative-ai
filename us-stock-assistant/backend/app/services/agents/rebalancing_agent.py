"""
Rebalancing Agent for portfolio composition analysis and rebalancing suggestions.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal

from app.services.portfolio_service import PortfolioService
from app.services.stock_data_service import StockDataService
from app.services.alert_service import AlertService
from app.models import Portfolio


class RebalancingAgent:
    """
    LangGraph agent for portfolio rebalancing analysis.
    Analyzes portfolio composition and generates rebalancing suggestions.
    """
    
    def __init__(self, db: Session, mcp_tools=None):
        self.db = db
        self.portfolio_service = PortfolioService(db)
        # Initialize stock service with MCP tools
        if mcp_tools is None:
            from app.mcp.tools.stock_data import StockDataMCPTools
            mcp_tools = StockDataMCPTools()
        self.stock_service = StockDataService(mcp_tools)
        self.alert_service = AlertService(db)
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the rebalancing agent.
        
        Args:
            state: Workflow state containing context and results
            
        Returns:
            Updated workflow state
        """
        results = state.get("results", {})
        errors = state.get("errors", [])
        context = state.get("context", {})
        
        try:
            # Get user_id from context
            user_id = context.get("user_id")
            if not user_id:
                errors.append("Rebalancing agent error: user_id not provided in context")
                state["results"] = results
                state["errors"] = errors
                return state
            
            # Get target allocations from context (optional)
            target_allocations = context.get("target_allocations", {})
            
            # Get user's portfolio
            from uuid import UUID
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.user_id == UUID(user_id)
            ).first()
            
            if not portfolio or not portfolio.positions:
                results["rebalancing"] = {
                    "suggestions": [],
                    "message": "No portfolio positions to analyze"
                }
                state["results"] = results
                return state
            
            # Analyze portfolio composition
            composition = await self._analyze_composition(portfolio)
            
            # Generate rebalancing suggestions
            suggestions = await self._generate_suggestions(
                portfolio,
                composition,
                target_allocations
            )
            
            # Store results as notification
            if suggestions:
                self.alert_service.send_notification(
                    user_id=UUID(user_id),
                    notification_type="rebalancing_suggestion",
                    title="Portfolio Rebalancing Suggestions",
                    message=f"Found {len(suggestions)} rebalancing opportunities",
                    data={
                        "suggestions": suggestions,
                        "composition": composition,
                        "analyzed_at": datetime.utcnow().isoformat()
                    }
                )
            
            results["rebalancing"] = {
                "composition": composition,
                "suggestions": suggestions,
                "suggestion_count": len(suggestions)
            }
            
        except Exception as e:
            errors.append(f"Rebalancing agent error: {str(e)}")
        
        state["results"] = results
        state["errors"] = errors
        state["current_node"] = "rebalancing_agent"
        
        return state
    
    async def _analyze_composition(self, portfolio: Portfolio) -> Dict[str, Any]:
        """
        Analyze current portfolio composition.
        
        Args:
            portfolio: Portfolio object
            
        Returns:
            Dictionary with composition analysis
        """
        # Get current prices for all positions
        tickers = [pos.ticker for pos in portfolio.positions]
        prices = await self.stock_service.getBatchPrices(tickers)
        
        # Calculate current values and allocations
        total_value = Decimal("0")
        position_values = {}
        
        for position in portfolio.positions:
            current_price = prices.get(position.ticker, {}).get("price", 0)
            value = Decimal(str(current_price)) * position.quantity
            position_values[position.ticker] = float(value)
            total_value += value
        
        # Calculate percentages
        allocations = {}
        for ticker, value in position_values.items():
            if total_value > 0:
                allocations[ticker] = (Decimal(str(value)) / total_value) * 100
            else:
                allocations[ticker] = Decimal("0")
        
        return {
            "total_value": float(total_value),
            "position_values": position_values,
            "allocations": {k: float(v) for k, v in allocations.items()},
            "position_count": len(portfolio.positions)
        }
    
    async def _generate_suggestions(
        self,
        portfolio: Portfolio,
        composition: Dict[str, Any],
        target_allocations: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Generate rebalancing suggestions.
        
        Args:
            portfolio: Portfolio object
            composition: Current composition analysis
            target_allocations: Target allocation percentages by ticker
            
        Returns:
            List of rebalancing suggestions
        """
        suggestions = []
        current_allocations = composition["allocations"]
        total_value = composition["total_value"]
        
        # If no target allocations provided, suggest equal weighting
        if not target_allocations:
            position_count = composition["position_count"]
            if position_count > 0:
                target_percent = 100.0 / position_count
                target_allocations = {
                    ticker: target_percent
                    for ticker in current_allocations.keys()
                }
        
        # Compare current vs target allocations
        for ticker, target_percent in target_allocations.items():
            current_percent = current_allocations.get(ticker, 0.0)
            difference = target_percent - current_percent
            
            # Only suggest rebalancing if difference is significant (>5%)
            if abs(difference) > 5.0:
                target_value = (Decimal(str(target_percent)) / 100) * Decimal(str(total_value))
                current_value = composition["position_values"].get(ticker, 0.0)
                amount_difference = float(target_value) - current_value
                
                if amount_difference > 0:
                    action = "buy"
                    reason = f"Underweight by {abs(difference):.1f}% (current: {current_percent:.1f}%, target: {target_percent:.1f}%)"
                else:
                    action = "sell"
                    reason = f"Overweight by {abs(difference):.1f}% (current: {current_percent:.1f}%, target: {target_percent:.1f}%)"
                
                suggestions.append({
                    "ticker": ticker,
                    "action": action,
                    "reason": reason,
                    "current_allocation": round(current_percent, 2),
                    "target_allocation": round(target_percent, 2),
                    "suggested_amount": round(abs(amount_difference), 2)
                })
        
        # Sort by magnitude of difference
        suggestions.sort(
            key=lambda x: abs(x["current_allocation"] - x["target_allocation"]),
            reverse=True
        )
        
        return suggestions
    
    async def analyze_portfolio(
        self,
        user_id: str,
        target_allocations: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Analyze a portfolio and generate rebalancing suggestions (public method).
        
        Args:
            user_id: User ID
            target_allocations: Optional target allocation percentages
            
        Returns:
            Dictionary with composition and suggestions
        """
        from uuid import UUID
        
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == UUID(user_id)
        ).first()
        
        if not portfolio or not portfolio.positions:
            return {
                "composition": {},
                "suggestions": [],
                "message": "No portfolio positions to analyze"
            }
        
        composition = await self._analyze_composition(portfolio)
        suggestions = await self._generate_suggestions(
            portfolio,
            composition,
            target_allocations or {}
        )
        
        return {
            "composition": composition,
            "suggestions": suggestions
        }
