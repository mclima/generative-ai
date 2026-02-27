"""
Price Alert Agent for monitoring stock prices and triggering alerts.
"""
from typing import Dict, Any, List
import asyncio
from sqlalchemy.orm import Session

from app.services.alert_service import AlertService
from app.services.stock_data_service import StockDataService


class PriceAlertAgent:
    """
    LangGraph agent for monitoring price alerts.
    Checks current prices against alert thresholds and triggers notifications.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)
        self.stock_service = StockDataService(db)
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the price alert agent.
        
        Args:
            state: Workflow state containing context and results
            
        Returns:
            Updated workflow state
        """
        results = state.get("results", {})
        errors = state.get("errors", [])
        
        try:
            # Get all active alerts
            active_alerts = self.alert_service.get_active_alerts()
            
            if not active_alerts:
                results["price_alerts"] = {
                    "checked": 0,
                    "triggered": 0,
                    "message": "No active alerts to check"
                }
                state["results"] = results
                return state
            
            # Group alerts by ticker for batch processing
            alerts_by_ticker = {}
            for alert in active_alerts:
                if alert.ticker not in alerts_by_ticker:
                    alerts_by_ticker[alert.ticker] = []
                alerts_by_ticker[alert.ticker].append(alert)
            
            # Check alerts in parallel
            triggered_alerts = await self._check_alerts_parallel(alerts_by_ticker)
            
            results["price_alerts"] = {
                "checked": len(active_alerts),
                "triggered": len(triggered_alerts),
                "alerts": triggered_alerts
            }
            
        except Exception as e:
            errors.append(f"Price alert agent error: {str(e)}")
        
        state["results"] = results
        state["errors"] = errors
        state["current_node"] = "price_alert_agent"
        
        return state
    
    async def _check_alerts_parallel(
        self,
        alerts_by_ticker: Dict[str, List]
    ) -> List[Dict[str, Any]]:
        """
        Check alerts in parallel for multiple tickers.
        
        Args:
            alerts_by_ticker: Dictionary mapping tickers to their alerts
            
        Returns:
            List of triggered alert details
        """
        tasks = []
        for ticker, alerts in alerts_by_ticker.items():
            tasks.append(self._check_ticker_alerts(ticker, alerts))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter out errors
        triggered_alerts = []
        for result in results:
            if isinstance(result, list):
                triggered_alerts.extend(result)
        
        return triggered_alerts
    
    async def _check_ticker_alerts(
        self,
        ticker: str,
        alerts: List
    ) -> List[Dict[str, Any]]:
        """
        Check all alerts for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            alerts: List of alerts for this ticker
            
        Returns:
            List of triggered alert details
        """
        triggered = []
        
        try:
            # Get current price
            price_data = await self.stock_service.get_current_price(ticker)
            current_price = price_data["price"]
            
            # Check each alert
            for alert in alerts:
                if self.alert_service.check_alert_condition(alert, current_price):
                    # Trigger the alert
                    trigger_result = self.alert_service.trigger_alert(alert, current_price)
                    triggered.append(trigger_result)
        
        except Exception as e:
            # Log error but don't fail the entire batch
            print(f"Error checking alerts for {ticker}: {str(e)}")
        
        return triggered
    
    async def check_single_alert(
        self,
        alert_id: str
    ) -> Dict[str, Any]:
        """
        Check a single alert by ID.
        
        Args:
            alert_id: UUID of the alert to check
            
        Returns:
            Dictionary with check results
        """
        from uuid import UUID
        from app.models import PriceAlert
        
        alert = self.db.query(PriceAlert).filter(
            PriceAlert.id == UUID(alert_id)
        ).first()
        
        if not alert:
            return {"error": f"Alert {alert_id} not found"}
        
        if not alert.is_active:
            return {"error": f"Alert {alert_id} is not active"}
        
        try:
            price_data = await self.stock_service.get_current_price(alert.ticker)
            current_price = price_data["price"]
            
            if self.alert_service.check_alert_condition(alert, current_price):
                trigger_result = self.alert_service.trigger_alert(alert, current_price)
                return {
                    "triggered": True,
                    "details": trigger_result
                }
            else:
                return {
                    "triggered": False,
                    "current_price": current_price,
                    "target_price": float(alert.target_price),
                    "condition": alert.condition
                }
        
        except Exception as e:
            return {"error": str(e)}
