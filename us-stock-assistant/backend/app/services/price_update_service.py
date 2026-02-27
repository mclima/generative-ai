"""
Price Update Service for broadcasting real-time stock prices.

This service runs a background task that fetches prices every 60 seconds
during market hours and broadcasts updates to WebSocket subscribers.
"""
import asyncio
import logging
from datetime import datetime, time
from typing import Set, Optional
from sqlalchemy.orm import Session

from app.services.websocket_service import get_websocket_service
from app.services.stock_data_service import StockDataService
from app.mcp.tools.stock_data import StockDataMCPTools
from app.database import SessionLocal

logger = logging.getLogger(__name__)


class PriceUpdateService:
    """
    Service for periodic price updates and broadcasting.
    
    Implements:
    - Background task running every 60 seconds during market hours
    - Fetches prices for all subscribed tickers
    - Broadcasts updates to WebSocket subscribers
    - Connection management and error handling
    """
    
    # US market hours (Eastern Time): 9:30 AM - 4:00 PM
    MARKET_OPEN_TIME = time(9, 30)
    MARKET_CLOSE_TIME = time(16, 0)
    
    # Update interval in seconds
    UPDATE_INTERVAL = 60
    
    def __init__(self):
        """Initialize Price Update Service."""
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    def is_market_hours(self) -> bool:
        """
        Check if current time is within market hours.
        
        Note: This is a simplified check. In production, you would:
        - Check against Eastern Time (ET) timezone
        - Account for market holidays
        - Handle pre-market and after-hours trading
        
        Returns:
            True if within market hours, False otherwise
        """
        # For now, always return True for testing
        # In production, implement proper market hours check
        now = datetime.utcnow().time()
        
        # Simple check (assumes UTC, needs timezone conversion in production)
        # Market hours: 9:30 AM - 4:00 PM ET = 14:30 - 21:00 UTC
        market_open_utc = time(14, 30)
        market_close_utc = time(21, 0)
        
        return market_open_utc <= now <= market_close_utc
    
    async def fetch_and_broadcast_prices(self) -> None:
        """
        Fetch prices for subscribed tickers and broadcast updates.
        
        This method:
        1. Gets all subscribed tickers from WebSocket service
        2. Fetches current prices for those tickers
        3. Broadcasts updates to subscribers
        """
        ws_service = get_websocket_service()
        
        # Get all subscribed tickers
        stats = ws_service.get_connection_stats()
        subscribed_tickers = stats.get("subscribed_tickers", [])
        
        if not subscribed_tickers:
            logger.debug("No subscribed tickers, skipping price update")
            return
        
        logger.info(f"Fetching prices for {len(subscribed_tickers)} tickers")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Initialize MCP tools and stock data service
            mcp_tools = StockDataMCPTools()
            stock_service = StockDataService(mcp_tools)
            
            # Fetch prices for all subscribed tickers
            prices = await stock_service.getBatchPrices(subscribed_tickers)
            
            # Broadcast each price update
            total_sent = 0
            for ticker, price_data in prices.items():
                sent_count = await ws_service.broadcastPriceUpdate(ticker, price_data)
                total_sent += sent_count
            
            logger.info(
                f"Broadcasted {len(prices)} price updates to {total_sent} total connections"
            )
        
        except Exception as e:
            logger.error(f"Error fetching and broadcasting prices: {e}")
        
        finally:
            db.close()
    
    async def run_update_loop(self) -> None:
        """
        Main loop for periodic price updates.
        
        Runs continuously, fetching and broadcasting prices every 60 seconds
        during market hours.
        """
        logger.info("Price update service started")
        
        while not self._stop_event.is_set():
            try:
                # Check if market is open
                if self.is_market_hours():
                    logger.debug("Market is open, fetching prices")
                    await self.fetch_and_broadcast_prices()
                else:
                    logger.debug("Market is closed, skipping price update")
                
                # Wait for next update interval or stop event
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.UPDATE_INTERVAL
                    )
                    # If we get here, stop event was set
                    break
                except asyncio.TimeoutError:
                    # Timeout is expected, continue loop
                    pass
            
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(10)
        
        logger.info("Price update service stopped")
    
    async def start(self) -> None:
        """
        Start the price update background task.
        
        This should be called when the application starts.
        """
        if self.is_running:
            logger.warning("Price update service is already running")
            return
        
        self.is_running = True
        self._stop_event.clear()
        self.task = asyncio.create_task(self.run_update_loop())
        logger.info("Price update service task created")
    
    async def stop(self) -> None:
        """
        Stop the price update background task.
        
        This should be called when the application shuts down.
        """
        if not self.is_running:
            logger.warning("Price update service is not running")
            return
        
        logger.info("Stopping price update service...")
        self.is_running = False
        self._stop_event.set()
        
        if self.task:
            try:
                await asyncio.wait_for(self.task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Price update service did not stop gracefully, cancelling")
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    pass
        
        logger.info("Price update service stopped")


# Global price update service instance
_price_update_service: Optional[PriceUpdateService] = None


def get_price_update_service() -> PriceUpdateService:
    """
    Get or create the global price update service instance.
    
    Returns:
        PriceUpdateService instance
    """
    global _price_update_service
    if _price_update_service is None:
        _price_update_service = PriceUpdateService()
    return _price_update_service
