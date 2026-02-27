"""
WebSocket router for real-time updates.

Provides WebSocket endpoint for stock price updates and notifications.
"""
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.websocket_service import get_websocket_service, WebSocketService
from app.services.auth_service import AuthService
from app.redis_client import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


async def authenticate_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Optional[str]:
    """
    Authenticate WebSocket connection using JWT token.
    
    Args:
        websocket: WebSocket connection
        token: JWT access token from query parameter
        db: Database session
    
    Returns:
        User ID if authenticated, None otherwise
    """
    if not token:
        logger.warning("WebSocket connection attempted without token")
        return None
    
    try:
        # Verify token
        redis_client = get_redis()
        auth_service = AuthService(db, redis_client)
        user = auth_service.verify_session(token)
        
        logger.info(f"WebSocket authenticated for user {user.id}")
        return str(user.id)
    
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        return None


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time updates.
    
    Protocol:
    - Client connects with JWT token in query parameter: /ws?token=<jwt_token>
    - Server authenticates and accepts connection
    - Client sends messages to subscribe/unsubscribe from tickers
    - Server broadcasts price updates and notifications
    
    Message formats:
    
    Client -> Server:
    {
        "action": "subscribe",
        "tickers": ["AAPL", "GOOGL", "MSFT"]
    }
    
    {
        "action": "unsubscribe",
        "tickers": ["AAPL"]
    }
    
    Server -> Client:
    {
        "type": "price_update",
        "ticker": "AAPL",
        "price": 150.25,
        "change": 2.50,
        "changePercent": 1.69,
        "volume": 50000000,
        "timestamp": "2024-01-15T10:30:00"
    }
    
    {
        "type": "notification",
        "notification": {
            "id": "uuid",
            "type": "price_alert",
            "title": "Price Alert: AAPL",
            "message": "AAPL is now above $150.00",
            "data": {...}
        },
        "timestamp": "2024-01-15T10:30:00"
    }
    
    Args:
        websocket: WebSocket connection
        token: JWT access token from query parameter
    """
    # Accept connection first
    await websocket.accept()
    
    # Authenticate using a temporary database session
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        user_id_str = await authenticate_websocket(websocket, token, db)
    finally:
        db.close()
    if not user_id_str:
        # Authentication failed - send error and close
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication failed"
            })
            await websocket.close(code=1008)
        except:
            pass
        return
    
    # Generate connection ID
    connection_id = str(uuid.uuid4())
    
    # Get WebSocket service
    ws_service = get_websocket_service()
    
    # Register connection
    try:
        # Convert user_id string to UUID
        user_id = uuid.UUID(user_id_str)
        connection = await ws_service.connect(connection_id, user_id, websocket)
        
        # Send welcome message
        await connection.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "message": "WebSocket connection established",
            "timestamp": connection.connected_at.isoformat()
        })
        
        # Handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                action = data.get("action")
                
                if action == "subscribe":
                    tickers = data.get("tickers", [])
                    if not isinstance(tickers, list):
                        await connection.send_json({
                            "type": "error",
                            "message": "tickers must be a list"
                        })
                        continue
                    
                    await ws_service.subscribeToStocks(connection, tickers)
                    logger.info(f"Connection {connection_id} subscribed to {tickers}")
                
                elif action == "unsubscribe":
                    tickers = data.get("tickers", [])
                    if not isinstance(tickers, list):
                        await connection.send_json({
                            "type": "error",
                            "message": "tickers must be a list"
                        })
                        continue
                    
                    await ws_service.unsubscribeFromStocks(connection, tickers)
                    logger.info(f"Connection {connection_id} unsubscribed from {tickers}")
                
                elif action == "ping":
                    # Heartbeat/keepalive
                    await connection.send_json({
                        "type": "pong",
                        "timestamp": connection.connected_at.isoformat()
                    })
                
                else:
                    await connection.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })
            
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                try:
                    await connection.send_json({
                        "type": "error",
                        "message": "Internal server error"
                    })
                except:
                    break
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {e}")
    
    finally:
        # Clean up connection
        await ws_service.disconnect(connection_id)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    
    Returns:
        Dictionary with connection statistics
    """
    ws_service = get_websocket_service()
    return ws_service.get_connection_stats()
