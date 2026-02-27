"""
Monitoring and observability module for the US Stock Assistant backend.

Provides:
- Prometheus metrics for performance monitoring
- Custom metrics for API latency, error rates, and MCP operations
"""

import os
import time
from typing import Optional, Callable
from functools import wraps

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Prometheus Metrics
# API Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# MCP Operation Metrics
mcp_requests_total = Counter(
    'mcp_requests_total',
    'Total MCP requests',
    ['server', 'tool', 'status']
)

mcp_request_duration_seconds = Histogram(
    'mcp_request_duration_seconds',
    'MCP request latency',
    ['server', 'tool']
)

mcp_errors_total = Counter(
    'mcp_errors_total',
    'Total MCP errors',
    ['server', 'tool', 'error_type']
)

# Agent Task Metrics
agent_tasks_total = Counter(
    'agent_tasks_total',
    'Total agent tasks executed',
    ['agent_type', 'status']
)

agent_task_duration_seconds = Histogram(
    'agent_task_duration_seconds',
    'Agent task execution time',
    ['agent_type']
)

# Database Metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query latency',
    ['operation']
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_key_prefix']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_key_prefix']
)

# WebSocket Metrics
websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections'
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['message_type']
)


def init_monitoring(environment: str = "development"):
    """
    Initialize monitoring for the application.
    
    Args:
        environment: Environment name (development, staging, production)
    """
    logger.info(f"Monitoring initialized for environment: {environment}")


def _sanitize_data(data):
    """
    Sanitize sensitive data from logs and metrics.
    
    Removes sensitive data like passwords, tokens, and API keys.
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in ['password', 'token', 'api_key', 'secret']):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        return sanitized
    return data


def track_mcp_request(server: str, tool: str):
    """
    Decorator to track MCP request metrics.
    
    Args:
        server: MCP server name (e.g., 'stock-data', 'news', 'market-data')
        tool: Tool name being invoked
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            error_type = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                error_type = type(e).__name__
                mcp_errors_total.labels(server=server, tool=tool, error_type=error_type).inc()
                raise
            finally:
                duration = time.time() - start_time
                mcp_requests_total.labels(server=server, tool=tool, status=status).inc()
                mcp_request_duration_seconds.labels(server=server, tool=tool).observe(duration)
        
        return wrapper
    return decorator


def track_agent_task(agent_type: str):
    """
    Decorator to track agent task execution metrics.
    
    Args:
        agent_type: Type of agent (e.g., 'price_alert', 'research', 'rebalancing')
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                agent_tasks_total.labels(agent_type=agent_type, status=status).inc()
                agent_task_duration_seconds.labels(agent_type=agent_type).observe(duration)
        
        return wrapper
    return decorator


def track_cache_operation(cache_key_prefix: str, hit: bool):
    """
    Track cache hit/miss metrics.
    
    Args:
        cache_key_prefix: Prefix of the cache key (e.g., 'stock:price', 'stock:news')
        hit: True if cache hit, False if cache miss
    """
    if hit:
        cache_hits_total.labels(cache_key_prefix=cache_key_prefix).inc()
    else:
        cache_misses_total.labels(cache_key_prefix=cache_key_prefix).inc()


def track_websocket_connection(connected: bool):
    """
    Track WebSocket connection changes.
    
    Args:
        connected: True if connection established, False if disconnected
    """
    if connected:
        websocket_connections_active.inc()
    else:
        websocket_connections_active.dec()


def track_websocket_message(message_type: str):
    """
    Track WebSocket message metrics.
    
    Args:
        message_type: Type of message (e.g., 'price_update', 'notification')
    """
    websocket_messages_total.labels(message_type=message_type).inc()


async def metrics_endpoint(request: Request) -> Response:
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus text format.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware:
    """
    Middleware to track HTTP request metrics.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        # Skip metrics endpoint to avoid recursion
        if path == "/metrics":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        status_code = 500  # Default to error
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.time() - start_time
            http_requests_total.labels(method=method, endpoint=path, status=status_code).inc()
            http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
