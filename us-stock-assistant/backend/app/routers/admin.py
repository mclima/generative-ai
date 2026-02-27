"""
Admin dashboard endpoints.

Provides system metrics, monitoring data, and operational insights.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.database import get_db
from app.redis_client import get_redis
from app.models import User, Portfolio, StockPosition, PriceAlert, Notification
from app.dependencies import get_current_user
from app.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


def is_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify that the current user has admin privileges.
    
    For now, this is a placeholder. In production, you would check
    a role or permission field on the user.
    """
    # TODO: Implement proper admin role checking
    # For now, allow all authenticated users (for development)
    return current_user


@router.get("/metrics")
async def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Get comprehensive system metrics.
    
    Returns:
    - User statistics
    - Portfolio statistics
    - Alert statistics
    - System health
    """
    try:
        # User metrics
        total_users = db.query(func.count(User.id)).scalar()
        users_last_24h = db.query(func.count(User.id)).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=1)
        ).scalar()
        users_last_7d = db.query(func.count(User.id)).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=7)
        ).scalar()
        
        # Portfolio metrics
        total_portfolios = db.query(func.count(Portfolio.id)).scalar()
        total_positions = db.query(func.count(StockPosition.id)).scalar()
        avg_positions_per_portfolio = db.query(
            func.avg(
                db.query(func.count(StockPosition.id))
                .filter(StockPosition.portfolio_id == Portfolio.id)
                .correlate(Portfolio)
                .scalar_subquery()
            )
        ).scalar() or 0
        
        # Alert metrics
        total_alerts = db.query(func.count(PriceAlert.id)).scalar()
        active_alerts = db.query(func.count(PriceAlert.id)).filter(
            PriceAlert.is_active == True
        ).scalar()
        triggered_alerts_24h = db.query(func.count(PriceAlert.id)).filter(
            PriceAlert.triggered_at >= datetime.utcnow() - timedelta(days=1)
        ).scalar()
        
        # Notification metrics
        total_notifications = db.query(func.count(Notification.id)).scalar()
        unread_notifications = db.query(func.count(Notification.id)).filter(
            Notification.is_read == False
        ).scalar()
        
        # Redis metrics
        redis_client = get_redis()
        redis_info = redis_client.info()
        redis_memory_mb = redis_info.get('used_memory', 0) / (1024 * 1024)
        redis_keys = await redis_client.dbsize()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "users": {
                "total": total_users,
                "last_24h": users_last_24h,
                "last_7d": users_last_7d,
            },
            "portfolios": {
                "total": total_portfolios,
                "total_positions": total_positions,
                "avg_positions_per_portfolio": round(float(avg_positions_per_portfolio), 2),
            },
            "alerts": {
                "total": total_alerts,
                "active": active_alerts,
                "triggered_last_24h": triggered_alerts_24h,
            },
            "notifications": {
                "total": total_notifications,
                "unread": unread_notifications,
            },
            "redis": {
                "memory_mb": round(redis_memory_mb, 2),
                "keys": redis_keys,
                "connected_clients": redis_info.get('connected_clients', 0),
            },
        }
    except Exception as e:
        logger.error(f"Failed to fetch system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system metrics")


@router.get("/api-usage")
async def get_api_usage(
    hours: int = 24,
    db: Session = Depends(get_db),
    current_user: User = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Get API usage statistics.
    
    Note: This is a simplified version. In production, you would track
    API calls in a separate table or use a time-series database.
    """
    try:
        # For now, return mock data
        # In production, you would query actual API usage logs
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "endpoints": [
                {
                    "endpoint": "/api/stocks/price",
                    "method": "GET",
                    "requests": 1250,
                    "avg_latency_ms": 45,
                    "error_rate": 0.02,
                },
                {
                    "endpoint": "/api/portfolio",
                    "method": "GET",
                    "requests": 890,
                    "avg_latency_ms": 120,
                    "error_rate": 0.01,
                },
                {
                    "endpoint": "/api/news",
                    "method": "GET",
                    "requests": 650,
                    "avg_latency_ms": 200,
                    "error_rate": 0.03,
                },
                {
                    "endpoint": "/api/analysis",
                    "method": "POST",
                    "requests": 320,
                    "avg_latency_ms": 3500,
                    "error_rate": 0.05,
                },
            ],
            "total_requests": 3110,
            "avg_latency_ms": 150,
            "overall_error_rate": 0.025,
        }
    except Exception as e:
        logger.error(f"Failed to fetch API usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch API usage")


@router.get("/mcp-status")
async def get_mcp_status(
    current_user: User = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Get MCP server status and statistics.
    
    Note: This is a simplified version. In production, you would track
    MCP operations in a separate table or monitoring system.
    """
    try:
        # For now, return mock data
        # In production, you would query actual MCP metrics
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "servers": [
                {
                    "name": "stock-data",
                    "status": "healthy",
                    "uptime_percent": 99.8,
                    "requests_24h": 5420,
                    "avg_latency_ms": 85,
                    "error_rate": 0.01,
                    "last_error": None,
                },
                {
                    "name": "news",
                    "status": "healthy",
                    "uptime_percent": 99.5,
                    "requests_24h": 2150,
                    "avg_latency_ms": 320,
                    "error_rate": 0.02,
                    "last_error": None,
                },
                {
                    "name": "market-data",
                    "status": "healthy",
                    "uptime_percent": 99.9,
                    "requests_24h": 1890,
                    "avg_latency_ms": 120,
                    "error_rate": 0.005,
                    "last_error": None,
                },
            ],
        }
    except Exception as e:
        logger.error(f"Failed to fetch MCP status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch MCP status")


@router.get("/agent-tasks")
async def get_agent_task_status(
    hours: int = 24,
    current_user: User = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Get agent task execution statistics.
    
    Note: This is a simplified version. In production, you would track
    agent tasks in a separate table.
    """
    try:
        # For now, return mock data
        # In production, you would query actual agent task logs
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "agents": [
                {
                    "type": "price_alert",
                    "tasks_executed": 145,
                    "tasks_succeeded": 142,
                    "tasks_failed": 3,
                    "avg_duration_ms": 250,
                    "last_execution": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                },
                {
                    "type": "research",
                    "tasks_executed": 28,
                    "tasks_succeeded": 27,
                    "tasks_failed": 1,
                    "avg_duration_ms": 8500,
                    "last_execution": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                },
                {
                    "type": "rebalancing",
                    "tasks_executed": 12,
                    "tasks_succeeded": 12,
                    "tasks_failed": 0,
                    "avg_duration_ms": 5200,
                    "last_execution": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                },
                {
                    "type": "news_monitor",
                    "tasks_executed": 96,
                    "tasks_succeeded": 94,
                    "tasks_failed": 2,
                    "avg_duration_ms": 1800,
                    "last_execution": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                },
            ],
            "total_tasks": 281,
            "success_rate": 0.979,
        }
    except Exception as e:
        logger.error(f"Failed to fetch agent task status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent task status")


@router.get("/error-log")
async def get_error_log(
    limit: int = 50,
    current_user: User = Depends(is_admin)
) -> Dict[str, Any]:
    """
    Get recent error log entries.
    
    Note: This is a simplified version. In production, you would query
    actual error logs from a logging system or database.
    """
    try:
        # For now, return mock data
        # In production, you would query actual error logs
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "limit": limit,
            "errors": [
                {
                    "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                    "level": "ERROR",
                    "source": "mcp_client",
                    "message": "Connection timeout to news server",
                    "count": 3,
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "level": "WARNING",
                    "source": "price_alert_agent",
                    "message": "Failed to send email notification",
                    "count": 1,
                },
                {
                    "timestamp": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
                    "level": "ERROR",
                    "source": "database",
                    "message": "Query timeout on portfolio metrics calculation",
                    "count": 2,
                },
            ],
        }
    except Exception as e:
        logger.error(f"Failed to fetch error log: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch error log")
