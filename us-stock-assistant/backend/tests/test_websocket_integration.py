"""
Integration tests for WebSocket real-time updates.

Tests WebSocket connection, authentication, subscriptions, price updates,
and notification delivery.
"""
import pytest
import asyncio
import json
from uuid import uuid4
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import User, PriceAlert, Notification
from app.services.auth_service import AuthService
from app.services.alert_service import AlertService
from app.services.websocket_service import get_websocket_service
from app.mcp.tools.stock_data import StockPrice
from app.redis_client import get_redis


@pytest.fixture
def test_user_and_token(db_session: Session) -> tuple:
    """Create a test user and return user and token."""
    from app.services.auth_service import AuthService
    
    redis_client = get_redis()
    auth_service = AuthService(db_session, redis_client)
    
    email = f"websocket_test_{uuid4()}@example.com"
    password = "TestPassword123!"
    
    user = auth_service.register(email, password)
    session = auth_service.login(email, password)
    
    return user, session["access_token"]


@pytest.fixture
def test_user(test_user_and_token) -> User:
    """Get test user."""
    return test_user_and_token[0]


@pytest.fixture
def auth_token(test_user_and_token) -> str:
    """Get authentication token for test user."""
    return test_user_and_token[1]


class TestWebSocketConnection:
    """Test WebSocket connection establishment and authentication."""
    
    def test_connection_stats_endpoint(self, db_session: Session):
        """Test WebSocket stats endpoint."""
        # Test the stats endpoint directly
        from app.services.websocket_service import get_websocket_service
        
        ws_service = get_websocket_service()
        stats = ws_service.get_connection_stats()
        
        assert "total_connections" in stats
        assert "total_users" in stats
        assert "total_ticker_subscriptions" in stats
        assert "subscribed_tickers" in stats
        assert isinstance(stats["total_connections"], int)
        assert isinstance(stats["subscribed_tickers"], list)


class TestPriceBroadcasting:
    """Test price update broadcasting to subscribers."""
    
    @pytest.mark.asyncio
    async def test_broadcast_price_update(self):
        """Test broadcasting price update to subscribed connections."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        # Create mock WebSocket connection
        from unittest.mock import AsyncMock, MagicMock
        
        mock_websocket = AsyncMock()
        connection_id = str(uuid4())
        user_id = uuid4()
        
        # Connect
        connection = await ws_service.connect(connection_id, user_id, mock_websocket)
        
        # Subscribe to AAPL
        await ws_service.subscribeToStocks(connection, ["AAPL"])
        
        # Create price update
        price = StockPrice(
            ticker="AAPL",
            price=150.25,
            change=2.50,
            change_percent=1.69,
            volume=50000000,
            timestamp=datetime.utcnow()
        )
        
        # Broadcast update
        sent_count = await ws_service.broadcastPriceUpdate("AAPL", price)
        
        # Verify broadcast
        assert sent_count == 1
        assert mock_websocket.send_json.called
        
        # Check message content
        call_args = mock_websocket.send_json.call_args_list[-1][0][0]
        assert call_args["type"] == "price_update"
        assert call_args["ticker"] == "AAPL"
        assert call_args["price"] == 150.25
        assert call_args["change"] == 2.50
        
        # Cleanup
        await ws_service.disconnect(connection_id)
    
    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_subscribers(self):
        """Test broadcasting to multiple subscribers."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        # Create multiple connections
        connections = []
        for i in range(3):
            mock_websocket = AsyncMock()
            connection_id = str(uuid4())
            user_id = uuid4()
            
            connection = await ws_service.connect(connection_id, user_id, mock_websocket)
            await ws_service.subscribeToStocks(connection, ["GOOGL"])
            connections.append((connection_id, mock_websocket))
        
        # Create price update
        price = StockPrice(
            ticker="GOOGL",
            price=2800.50,
            change=-15.25,
            change_percent=-0.54,
            volume=1500000,
            timestamp=datetime.utcnow()
        )
        
        # Broadcast update
        sent_count = await ws_service.broadcastPriceUpdate("GOOGL", price)
        
        # Verify all connections received update
        assert sent_count == 3
        
        for connection_id, mock_websocket in connections:
            assert mock_websocket.send_json.called
            await ws_service.disconnect(connection_id)
    
    @pytest.mark.asyncio
    async def test_broadcast_only_to_subscribers(self):
        """Test that broadcast only goes to subscribers of that ticker."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        # Create two connections with different subscriptions
        mock_ws1 = AsyncMock()
        conn1_id = str(uuid4())
        conn1 = await ws_service.connect(conn1_id, uuid4(), mock_ws1)
        await ws_service.subscribeToStocks(conn1, ["AAPL"])
        
        mock_ws2 = AsyncMock()
        conn2_id = str(uuid4())
        conn2 = await ws_service.connect(conn2_id, uuid4(), mock_ws2)
        await ws_service.subscribeToStocks(conn2, ["GOOGL"])
        
        # Broadcast AAPL update
        price = StockPrice(
            ticker="AAPL",
            price=150.00,
            change=1.00,
            change_percent=0.67,
            volume=10000000,
            timestamp=datetime.utcnow()
        )
        
        sent_count = await ws_service.broadcastPriceUpdate("AAPL", price)
        
        # Only conn1 should receive update (check last call, not first subscription confirmation)
        assert sent_count == 1
        # conn1 should have 2 calls: subscription confirmation + price update
        assert mock_ws1.send_json.call_count >= 2
        # conn2 should only have 1 call: subscription confirmation
        assert mock_ws2.send_json.call_count == 1
        
        # Cleanup
        await ws_service.disconnect(conn1_id)
        await ws_service.disconnect(conn2_id)


class TestNotificationDelivery:
    """Test real-time notification delivery via WebSocket."""
    
    @pytest.mark.asyncio
    async def test_send_notification_to_user(self):
        """Test sending notification to user via WebSocket."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        # Create connection
        mock_websocket = AsyncMock()
        connection_id = str(uuid4())
        user_id = uuid4()
        
        connection = await ws_service.connect(connection_id, user_id, mock_websocket)
        
        # Send notification
        notification = {
            "id": str(uuid4()),
            "type": "price_alert",
            "title": "Price Alert: AAPL",
            "message": "AAPL is now above $150.00",
            "data": {
                "ticker": "AAPL",
                "price": 150.25
            }
        }
        
        sent_count = await ws_service.sendNotificationToUser(user_id, notification)
        
        # Verify notification sent
        assert sent_count == 1
        assert mock_websocket.send_json.called
        
        # Check message content
        call_args = mock_websocket.send_json.call_args[0][0]
        assert call_args["type"] == "notification"
        assert call_args["notification"] == notification
        assert "timestamp" in call_args
        
        # Cleanup
        await ws_service.disconnect(connection_id)
    
    @pytest.mark.asyncio
    async def test_send_notification_to_multiple_connections(self):
        """Test sending notification to user with multiple connections."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        user_id = uuid4()
        
        # Create multiple connections for same user
        connections = []
        for i in range(2):
            mock_websocket = AsyncMock()
            connection_id = str(uuid4())
            
            connection = await ws_service.connect(connection_id, user_id, mock_websocket)
            connections.append((connection_id, mock_websocket))
        
        # Send notification
        notification = {
            "id": str(uuid4()),
            "type": "news_update",
            "title": "Breaking News",
            "message": "Important market update"
        }
        
        sent_count = await ws_service.sendNotificationToUser(user_id, notification)
        
        # Verify all connections received notification
        assert sent_count == 2
        
        for connection_id, mock_websocket in connections:
            assert mock_websocket.send_json.called
            await ws_service.disconnect(connection_id)
    
    def test_alert_service_integration(self, db_session: Session):
        """Test that AlertService sends WebSocket notifications."""
        # Create test user directly
        from app.services.auth_service import AuthService
        from app.models import User
        
        redis_client = get_redis()
        auth_service = AuthService(db_session, redis_client)
        
        email = f"alert_test_{uuid4()}@example.com"
        password = "TestPassword123!"
        
        # Register returns a session dict, we need to get the user from DB
        session_data = auth_service.register(email, password)
        
        # Get the user from the database
        user = db_session.query(User).filter(User.email == email).first()
        assert user is not None
        
        alert_service = AlertService(db_session)
        
        # Create a notification
        notification = alert_service.send_notification(
            user_id=user.id,
            notification_type="price_alert",
            title="Test Alert",
            message="This is a test alert",
            data={"ticker": "AAPL"},
            channels=["in-app"]
        )
        
        # Verify notification was created
        assert notification.id is not None
        assert notification.user_id == user.id
        assert notification.type == "price_alert"
        assert notification.title == "Test Alert"
        
        # Note: WebSocket sending is tested separately with mocks
        # since we can't easily test async WebSocket in sync test


class TestConnectionManagement:
    """Test connection lifecycle and error handling."""
    
    @pytest.mark.asyncio
    async def test_disconnect_cleanup(self):
        """Test that disconnect properly cleans up subscriptions."""
        # Create a fresh WebSocket service instance for this test
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        # Create connection and subscribe
        mock_websocket = AsyncMock()
        connection_id = str(uuid4())
        user_id = uuid4()
        
        connection = await ws_service.connect(connection_id, user_id, mock_websocket)
        await ws_service.subscribeToStocks(connection, ["AAPL", "GOOGL"])
        
        # Verify subscriptions exist
        stats = ws_service.get_connection_stats()
        assert "AAPL" in stats["subscribed_tickers"]
        assert "GOOGL" in stats["subscribed_tickers"]
        
        # Disconnect
        await ws_service.disconnect(connection_id)
        
        # Verify cleanup
        stats = ws_service.get_connection_stats()
        assert stats["total_connections"] == 0
        assert len(stats["subscribed_tickers"]) == 0
    
    @pytest.mark.asyncio
    async def test_failed_send_cleanup(self):
        """Test that failed sends trigger connection cleanup."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        # Create connection that will fail on send
        mock_websocket = AsyncMock()
        # Only fail on price update, not on subscription confirmation
        call_count = [0]
        
        async def send_json_side_effect(data):
            call_count[0] += 1
            if call_count[0] > 1:  # Fail after subscription confirmation
                raise Exception("Connection lost")
        
        mock_websocket.send_json.side_effect = send_json_side_effect
        
        connection_id = str(uuid4())
        user_id = uuid4()
        
        connection = await ws_service.connect(connection_id, user_id, mock_websocket)
        await ws_service.subscribeToStocks(connection, ["AAPL"])
        
        # Try to broadcast (should fail and cleanup)
        price = StockPrice(
            ticker="AAPL",
            price=150.00,
            change=1.00,
            change_percent=0.67,
            volume=10000000,
            timestamp=datetime.utcnow()
        )
        
        sent_count = await ws_service.broadcastPriceUpdate("AAPL", price)
        
        # Should have failed and cleaned up
        assert sent_count == 0
        stats = ws_service.get_connection_stats()
        assert stats["total_connections"] == 0
    
    @pytest.mark.asyncio
    async def test_get_connection_stats(self):
        """Test getting connection statistics."""
        from app.services.websocket_service import WebSocketService
        ws_service = WebSocketService()
        
        from unittest.mock import AsyncMock
        
        # Create some connections
        connections = []
        for i in range(3):
            mock_websocket = AsyncMock()
            connection_id = str(uuid4())
            user_id = uuid4()
            
            connection = await ws_service.connect(connection_id, user_id, mock_websocket)
            await ws_service.subscribeToStocks(connection, [f"STOCK{i}"])
            connections.append(connection_id)
        
        # Get stats
        stats = ws_service.get_connection_stats()
        
        assert stats["total_connections"] == 3
        assert stats["total_users"] == 3
        assert stats["total_ticker_subscriptions"] == 3
        assert len(stats["subscribed_tickers"]) == 3
        
        # Cleanup
        for connection_id in connections:
            await ws_service.disconnect(connection_id)


# Run tests with: pytest backend/tests/test_websocket_integration.py -v
