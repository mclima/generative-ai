"""
Smoke tests for API endpoints - validates basic structure and imports.

These tests verify that all routers are properly configured and
endpoints are accessible without requiring full integration setup.
"""
import pytest
from fastapi.testclient import TestClient


def test_app_imports():
    """Test that the app can be imported without errors."""
    try:
        from app.main import app
        assert app is not None
        assert app.title == "US Stock Assistant API"
    except ImportError as e:
        pytest.fail(f"Failed to import app: {e}")


def test_routers_registered():
    """Test that all routers are registered with the app."""
    from app.main import app
    
    # Get all registered routes
    routes = [route.path for route in app.routes]
    
    # Check auth endpoints
    assert "/api/auth/register" in routes
    assert "/api/auth/login" in routes
    assert "/api/auth/logout" in routes
    assert "/api/auth/refresh" in routes
    assert "/api/auth/me" in routes
    
    # Check portfolio endpoints
    assert "/api/portfolio" in routes
    assert "/api/portfolio/positions" in routes
    assert "/api/portfolio/metrics" in routes
    assert "/api/portfolio/export" in routes
    assert "/api/portfolio/import" in routes
    
    # Check stock endpoints
    assert "/api/stocks/search" in routes
    assert "/api/stocks/{ticker}" in routes
    assert "/api/stocks/{ticker}/price" in routes
    assert "/api/stocks/{ticker}/historical" in routes
    assert "/api/stocks/{ticker}/company" in routes
    assert "/api/stocks/{ticker}/metrics" in routes
    
    # Check news and market endpoints
    assert "/api/news/stock/{ticker}" in routes
    assert "/api/news/market" in routes
    assert "/api/market/overview" in routes
    assert "/api/market/trending" in routes
    assert "/api/market/sectors" in routes
    assert "/api/market/indices" in routes
    
    # Check analysis endpoints
    assert "/api/analysis/stock/{ticker}" in routes
    assert "/api/analysis/portfolio" in routes
    
    # Check alert endpoints
    assert "/api/alerts" in routes
    assert "/api/notifications" in routes
    
    # Check preferences endpoints
    assert "/api/preferences" in routes
    assert "/api/preferences/reset" in routes


def test_endpoint_methods():
    """Test that endpoints have correct HTTP methods."""
    from app.main import app
    
    # Find routes by path and check methods
    routes_by_path = {}
    for route in app.routes:
        if hasattr(route, 'methods'):
            if route.path not in routes_by_path:
                routes_by_path[route.path] = set()
            routes_by_path[route.path].update(route.methods)
    
    # Auth endpoints
    assert 'POST' in routes_by_path.get('/api/auth/register', set())
    assert 'POST' in routes_by_path.get('/api/auth/login', set())
    assert 'POST' in routes_by_path.get('/api/auth/logout', set())
    assert 'GET' in routes_by_path.get('/api/auth/me', set())
    
    # Portfolio endpoints
    assert 'GET' in routes_by_path.get('/api/portfolio', set())
    assert 'POST' in routes_by_path.get('/api/portfolio/positions', set())
    assert 'GET' in routes_by_path.get('/api/portfolio/metrics', set())
    
    # Stock endpoints
    assert 'GET' in routes_by_path.get('/api/stocks/search', set())
    assert 'GET' in routes_by_path.get('/api/stocks/{ticker}', set())
    
    # Analysis endpoints
    assert 'POST' in routes_by_path.get('/api/analysis/stock/{ticker}', set())
    assert 'POST' in routes_by_path.get('/api/analysis/portfolio', set())
    
    # Alert endpoints
    assert 'GET' in routes_by_path.get('/api/alerts', set())
    assert 'POST' in routes_by_path.get('/api/alerts', set())
    
    # Preferences endpoints
    assert 'GET' in routes_by_path.get('/api/preferences', set())
    assert 'PUT' in routes_by_path.get('/api/preferences', set())
    assert 'POST' in routes_by_path.get('/api/preferences/reset', set())


def test_pydantic_models():
    """Test that Pydantic models are properly defined."""
    # Auth models
    from app.routers.auth import RegisterRequest, LoginRequest, AuthResponse
    assert RegisterRequest is not None
    assert LoginRequest is not None
    assert AuthResponse is not None
    
    # Portfolio models
    from app.routers.portfolio import StockPositionInput, PortfolioResponse
    assert StockPositionInput is not None
    assert PortfolioResponse is not None
    
    # Stock models
    from app.routers.stocks import StockPriceResponse, CompanyInfoResponse
    assert StockPriceResponse is not None
    assert CompanyInfoResponse is not None
    
    # Alert models
    from app.routers.alerts import PriceAlertInput, NotificationResponse
    assert PriceAlertInput is not None
    assert NotificationResponse is not None
    
    # Preferences models
    from app.routers.preferences import UserPreferencesInput, UserPreferencesResponse
    assert UserPreferencesInput is not None
    assert UserPreferencesResponse is not None


def test_middleware_configured():
    """Test that middleware is properly configured."""
    from app.main import app
    
    # Check that middleware is registered
    middleware_types = [type(m).__name__ for m in app.user_middleware]
    
    # Should have CORS, Auth, and Error Handler middleware
    assert len(middleware_types) > 0


def test_health_endpoint():
    """Test that health check endpoint exists."""
    from app.main import app
    
    routes = [route.path for route in app.routes]
    assert "/health" in routes


def test_openapi_schema():
    """Test that OpenAPI schema is generated."""
    from app.main import app
    
    schema = app.openapi()
    assert schema is not None
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "US Stock Assistant API"
    assert "paths" in schema
    
    # Check that major endpoint groups are in schema
    paths = schema["paths"]
    assert any("/api/auth/" in path for path in paths)
    assert any("/api/portfolio" in path for path in paths)
    assert any("/api/stocks/" in path for path in paths)
    assert any("/api/analysis/" in path for path in paths)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
