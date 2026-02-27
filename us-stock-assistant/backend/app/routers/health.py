"""
Health check and system status endpoints.

Provides detailed health information about the application and its dependencies.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
import time
from datetime import datetime

from app.database import get_db
from app.redis_client import get_redis
from app.mcp.factory import get_mcp_factory
from app.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns a simple status indicating the service is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "us-stock-assistant-api"
    }


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with dependency status.
    
    Checks:
    - Database connectivity
    - Redis connectivity
    - MCP server connectivity
    
    Returns detailed status for each component.
    """
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "us-stock-assistant-api",
        "checks": {}
    }
    
    # Check database
    db_status = await _check_database(db)
    health_status["checks"]["database"] = db_status
    
    # Check Redis
    redis_status = await _check_redis()
    health_status["checks"]["redis"] = redis_status
    
    # Check MCP servers
    mcp_status = await _check_mcp_servers()
    health_status["checks"]["mcp_servers"] = mcp_status
    
    # Determine overall status
    all_healthy = all(
        check.get("status") == "healthy" 
        for check in health_status["checks"].values()
        if isinstance(check, dict)
    )
    
    if not all_healthy:
        health_status["status"] = "degraded"
    
    # Add response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_status


async def _check_database(db: Session) -> Dict[str, Any]:
    """Check database connectivity and responsiveness."""
    try:
        start_time = time.time()
        db.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Database connection failed"
        }


async def _check_redis() -> Dict[str, Any]:
    """Check Redis connectivity and responsiveness."""
    try:
        redis_client = get_redis()
        start_time = time.time()
        redis_client.ping()
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis connection failed"
        }


async def _check_mcp_servers() -> Dict[str, Any]:
    """Check MCP server connectivity."""
    mcp_factory = get_mcp_factory()
    servers = {
        "stock-data": mcp_factory.get_stock_data_client(),
        "news": mcp_factory.get_news_client(),
        "market-data": mcp_factory.get_market_data_client()
    }
    
    server_status = {}
    all_healthy = True
    
    for server_name, client in servers.items():
        try:
            start_time = time.time()
            # Try to list tools as a connectivity check
            tools = await client.list_tools()
            latency_ms = round((time.time() - start_time) * 1000, 2)
            
            server_status[server_name] = {
                "status": "healthy",
                "latency_ms": latency_ms,
                "tools_count": len(tools) if tools else 0,
                "message": f"{server_name} server operational"
            }
        except Exception as e:
            logger.error(f"MCP server {server_name} health check failed: {e}")
            all_healthy = False
            server_status[server_name] = {
                "status": "unhealthy",
                "error": str(e),
                "message": f"{server_name} server unavailable"
            }
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "servers": server_status
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe for Kubernetes/container orchestration.
    
    Returns 200 if the service is ready to accept traffic, 503 otherwise.
    """
    try:
        # Check critical dependencies
        db.execute(text("SELECT 1"))
        redis_client = get_redis()
        redis_client.ping()
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes/container orchestration.
    
    Returns 200 if the service is alive (even if dependencies are down).
    """
    return {"status": "alive"}
