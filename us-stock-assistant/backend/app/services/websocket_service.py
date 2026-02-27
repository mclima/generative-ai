"""
WebSocket Service for managing real-time connections and updates.

This service handles WebSocket connections, stock price subscriptions,
and real-time notification delivery.
"""
import asyncio
import logging
from typing import Dict, Set, Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import json

from app.mcp.tools.stock_data import StockPrice

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Represents a WebSocket connection with subscription management."""
    
    def __init__(self, connection_id: str, user_id: UUID, websocket: WebSocket):
        """
        Initialize WebSocket connection.
        
        Args:
            connection_id: Unique connection identifier
            user_id: UUID of the authenticated user
            websocket: FastAPI WebSocket instance
        """
        self.id = connection_id
        self.user_id = user_id
        self.socket = websocket
        self.subscribed_tickers: Set[str] = set()
        self.connected_at = datetime.utcnow()
    
    async def send_json(self, data: dict) -> None:
        """
        Send JSON data through the WebSocket.
        
        Args:
            data: Dictionary to send as JSON
        """
        try:
            await self.socket.send_json(data)
        except Exception as e:
            logger.error(f"Failed to send data to connection {self.id}: {e}")
            raise
    
    async def send_text(self, message: str) -> None:
        """
        Send text message through the WebSocket.
        
        Args:
            message: Text message to send
        """
        try:
            await self.socket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send text to connection {self.id}: {e}")
            raise


class WebSocketService:
    """
    Service for managing WebSocket connections and broadcasting updates.
    
    Implements:
    - Connection management with authentication
    - Stock price subscription/unsubscription
    - Price update broadcasting to subscribers
    - Real-time notification delivery
    """
    
    def __init__(self):
        """Initialize WebSocket service."""
        # Map of connection_id -> WebSocketConnection
        self.active_connections: Dict[str, WebSocketConnection] = {}
        
        # Map of user_id -> Set of connection_ids
        self.user_connections: Dict[UUID, Set[str]] = {}
        
        # Map of ticker -> Set of connection_ids subscribed to that ticker
        self.ticker_subscriptions: Dict[str, Set[str]] = {}
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(
        self,
        connection_id: str,
        user_id: UUID,
        websocket: WebSocket
    ) -> WebSocketConnection:
        """
        Establish a new WebSocket connection.
        
        Args:
            connection_id: Unique connection identifier
            user_id: UUID of the authenticated user
            websocket: FastAPI WebSocket instance
        
        Returns:
            WebSocketConnection instance
        """
        async with self._lock:
            # Create connection object
            connection = WebSocketConnection(connection_id, user_id, websocket)
            
            # Store connection
            self.active_connections[connection_id] = connection
            
            # Track user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            
            logger.info(
                f"WebSocket connected: connection_id={connection_id}, "
                f"user_id={user_id}, total_connections={len(self.active_connections)}"
            )
            
            return connection
    
    async def disconnect(self, connection_id: str) -> None:
        """
        Disconnect and clean up a WebSocket connection.
        
        Args:
            connection_id: Connection identifier to disconnect
        """
        async with self._lock:
            connection = self.active_connections.get(connection_id)
            if not connection:
                logger.warning(f"Attempted to disconnect non-existent connection: {connection_id}")
                return
            
            # Unsubscribe from all tickers
            for ticker in list(connection.subscribed_tickers):
                await self._unsubscribe_ticker(connection_id, ticker)
            
            # Remove from user connections
            user_id = connection.user_id
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove connection
            del self.active_connections[connection_id]
            
            logger.info(
                f"WebSocket disconnected: connection_id={connection_id}, "
                f"user_id={user_id}, remaining_connections={len(self.active_connections)}"
            )
    
    async def subscribeToStocks(
        self,
        connection: WebSocketConnection,
        tickers: List[str]
    ) -> None:
        """
        Subscribe a connection to stock price updates.
        
        Args:
            connection: WebSocketConnection instance
            tickers: List of stock ticker symbols to subscribe to
        """
        async with self._lock:
            for ticker in tickers:
                ticker = ticker.upper()
                
                # Add to connection's subscriptions
                connection.subscribed_tickers.add(ticker)
                
                # Add to ticker subscriptions
                if ticker not in self.ticker_subscriptions:
                    self.ticker_subscriptions[ticker] = set()
                self.ticker_subscriptions[ticker].add(connection.id)
                
                logger.debug(
                    f"Connection {connection.id} subscribed to {ticker}. "
                    f"Total subscribers for {ticker}: {len(self.ticker_subscriptions[ticker])}"
                )
        
        # Send confirmation
        await connection.send_json({
            "type": "subscription_confirmed",
            "tickers": tickers,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def unsubscribeFromStocks(
        self,
        connection: WebSocketConnection,
        tickers: List[str]
    ) -> None:
        """
        Unsubscribe a connection from stock price updates.
        
        Args:
            connection: WebSocketConnection instance
            tickers: List of stock ticker symbols to unsubscribe from
        """
        async with self._lock:
            for ticker in tickers:
                ticker = ticker.upper()
                await self._unsubscribe_ticker(connection.id, ticker)
        
        # Send confirmation
        await connection.send_json({
            "type": "unsubscription_confirmed",
            "tickers": tickers,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _unsubscribe_ticker(self, connection_id: str, ticker: str) -> None:
        """
        Internal method to unsubscribe a connection from a ticker.
        
        Args:
            connection_id: Connection identifier
            ticker: Stock ticker symbol
        """
        ticker = ticker.upper()
        
        # Remove from connection's subscriptions
        connection = self.active_connections.get(connection_id)
        if connection:
            connection.subscribed_tickers.discard(ticker)
        
        # Remove from ticker subscriptions
        if ticker in self.ticker_subscriptions:
            self.ticker_subscriptions[ticker].discard(connection_id)
            if not self.ticker_subscriptions[ticker]:
                del self.ticker_subscriptions[ticker]
            
            logger.debug(
                f"Connection {connection_id} unsubscribed from {ticker}. "
                f"Remaining subscribers: {len(self.ticker_subscriptions.get(ticker, set()))}"
            )
    
    async def broadcastPriceUpdate(self, ticker: str, price: StockPrice) -> int:
        """
        Broadcast price update to all subscribers of a ticker.
        
        Args:
            ticker: Stock ticker symbol
            price: StockPrice object with current price data
        
        Returns:
            Number of connections that received the update
        """
        ticker = ticker.upper()
        
        # Get subscribers for this ticker
        subscriber_ids = self.ticker_subscriptions.get(ticker, set()).copy()
        
        if not subscriber_ids:
            logger.debug(f"No subscribers for {ticker}, skipping broadcast")
            return 0
        
        # Prepare message
        message = {
            "type": "price_update",
            "ticker": ticker,
            "price": price.price,
            "change": price.change,
            "changePercent": price.change_percent,
            "volume": price.volume,
            "timestamp": price.timestamp.isoformat()
        }
        
        # Broadcast to all subscribers
        sent_count = 0
        failed_connections = []
        
        for connection_id in subscriber_ids:
            connection = self.active_connections.get(connection_id)
            if not connection:
                failed_connections.append(connection_id)
                continue
            
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send price update to {connection_id}: {e}")
                failed_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
        
        logger.debug(
            f"Broadcasted {ticker} price update to {sent_count} connections "
            f"({len(failed_connections)} failed)"
        )
        
        return sent_count
    
    async def sendNotificationToUser(
        self,
        user_id: UUID,
        notification: dict
    ) -> int:
        """
        Send notification to all connections of a specific user.
        
        Args:
            user_id: UUID of the user
            notification: Notification data dictionary
        
        Returns:
            Number of connections that received the notification
        """
        # Get all connections for this user
        connection_ids = self.user_connections.get(user_id, set()).copy()
        
        if not connection_ids:
            logger.debug(f"No active connections for user {user_id}, skipping notification")
            return 0
        
        # Prepare message
        message = {
            "type": "notification",
            "notification": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to all user connections
        sent_count = 0
        failed_connections = []
        
        for connection_id in connection_ids:
            connection = self.active_connections.get(connection_id)
            if not connection:
                failed_connections.append(connection_id)
                continue
            
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send notification to {connection_id}: {e}")
                failed_connections.append(connection_id)
        
        # Clean up failed connections
        for connection_id in failed_connections:
            await self.disconnect(connection_id)
        
        logger.info(
            f"Sent notification to user {user_id}: {sent_count} connections "
            f"({len(failed_connections)} failed)"
        )
        
        return sent_count
    
    def get_connection_stats(self) -> dict:
        """
        Get statistics about active connections.
        
        Returns:
            Dictionary with connection statistics
        """
        return {
            "total_connections": len(self.active_connections),
            "total_users": len(self.user_connections),
            "total_ticker_subscriptions": len(self.ticker_subscriptions),
            "subscribed_tickers": list(self.ticker_subscriptions.keys())
        }
    
    def get_user_connection_count(self, user_id: UUID) -> int:
        """
        Get number of active connections for a user.
        
        Args:
            user_id: UUID of the user
        
        Returns:
            Number of active connections
        """
        return len(self.user_connections.get(user_id, set()))


# Global WebSocket service instance
_websocket_service: Optional[WebSocketService] = None


def get_websocket_service() -> WebSocketService:
    """
    Get or create the global WebSocket service instance.
    
    Returns:
        WebSocketService instance
    """
    global _websocket_service
    if _websocket_service is None:
        _websocket_service = WebSocketService()
    return _websocket_service
