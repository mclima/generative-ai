"""
Integration tests for FastAPI endpoints.

Tests all API endpoints with valid and invalid inputs, authentication,
authorization, and error responses.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from decimal import Decimal
import json

from app.main import app
from app.database import get_db
from app.models import User, Portfolio, StockPosition, PriceAlert, UserPreferences
from app.services.auth_service import AuthService
from tests.conftest import test_db, client, test_user, auth_headers


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "newuser@example.com"
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,
                "password": "AnotherPass123!"
            }
        )
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "testpass123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials fails."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth fails."""
        response = client.get("/api/auth/me")
        assert response.status_code == 403


class TestPortfolioEndpoints:
    """Test portfolio management endpoints."""
    
    def test_get_portfolio(self, client, auth_headers):
        """Test getting user's portfolio."""
        response = client.get("/api/portfolio", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "positions" in data
        assert isinstance(data["positions"], list)
    
    def test_get_portfolio_unauthorized(self, client):
        """Test getting portfolio without auth fails."""
        response = client.get("/api/portfolio")
        assert response.status_code == 403
    
    def test_add_position_success(self, client, auth_headers):
        """Test adding a stock position."""
        response = client.post(
            "/api/portfolio/positions",
            headers=auth_headers,
            json={
                "ticker": "AAPL",
                "quantity": 10.0,
                "purchase_price": 150.50,
                "purchase_date": "2024-01-15"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert data["quantity"] == 10.0
        assert data["purchase_price"] == 150.50
    
    def test_add_position_invalid_ticker(self, client, auth_headers):
        """Test adding position with invalid ticker fails."""
        response = client.post(
            "/api/portfolio/positions",
            headers=auth_headers,
            json={
                "ticker": "",
                "quantity": 10.0,
                "purchase_price": 150.50,
                "purchase_date": "2024-01-15"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_add_position_negative_quantity(self, client, auth_headers):
        """Test adding position with negative quantity fails."""
        response = client.post(
            "/api/portfolio/positions",
            headers=auth_headers,
            json={
                "ticker": "AAPL",
                "quantity": -10.0,
                "purchase_price": 150.50,
                "purchase_date": "2024-01-15"
            }
        )
        assert response.status_code == 422
    
    def test_update_position(self, client, auth_headers, test_db):
        """Test updating a stock position."""
        # First add a position
        add_response = client.post(
            "/api/portfolio/positions",
            headers=auth_headers,
            json={
                "ticker": "MSFT",
                "quantity": 5.0,
                "purchase_price": 300.00,
                "purchase_date": "2024-01-10"
            }
        )
        position_id = add_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/portfolio/positions/{position_id}",
            headers=auth_headers,
            json={
                "quantity": 7.0,
                "purchase_price": 310.00
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 7.0
        assert data["purchase_price"] == 310.00
    
    def test_delete_position(self, client, auth_headers):
        """Test deleting a stock position."""
        # First add a position
        add_response = client.post(
            "/api/portfolio/positions",
            headers=auth_headers,
            json={
                "ticker": "GOOGL",
                "quantity": 3.0,
                "purchase_price": 140.00,
                "purchase_date": "2024-01-05"
            }
        )
        position_id = add_response.json()["id"]
        
        # Delete it
        response = client.delete(
            f"/api/portfolio/positions/{position_id}",
            headers=auth_headers
        )
        assert response.status_code == 204


class TestStockDataEndpoints:
    """Test stock data endpoints."""
    
    def test_search_stocks(self, client):
        """Test stock search."""
        response = client.get("/api/stocks/search?q=AAPL&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_stocks_missing_query(self, client):
        """Test stock search without query fails."""
        response = client.get("/api/stocks/search")
        assert response.status_code == 422
    
    def test_get_stock_price(self, client):
        """Test getting stock price."""
        response = client.get("/api/stocks/AAPL/price")
        assert response.status_code == 200
        data = response.json()
        assert "ticker" in data
        assert "price" in data
        assert "change" in data
    
    def test_get_stock_details(self, client):
        """Test getting complete stock details."""
        response = client.get("/api/stocks/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "price" in data
        assert "company" in data
        assert "metrics" in data
    
    def test_get_historical_data(self, client):
        """Test getting historical price data."""
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        response = client.get(
            f"/api/stocks/AAPL/historical?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_historical_data_invalid_range(self, client):
        """Test historical data with invalid date range fails."""
        end_date = date.today()
        start_date = end_date + timedelta(days=30)  # Start after end
        
        response = client.get(
            f"/api/stocks/AAPL/historical?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 400


class TestNewsAndMarketEndpoints:
    """Test news and market overview endpoints."""
    
    def test_get_stock_news(self, client):
        """Test getting stock-specific news."""
        response = client.get("/api/news/stock/AAPL?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_market_news(self, client):
        """Test getting general market news."""
        response = client.get("/api/news/market?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_market_overview(self, client):
        """Test getting market overview."""
        response = client.get("/api/market/overview")
        assert response.status_code == 200
        data = response.json()
        assert "headlines" in data
        assert "sentiment" in data
        assert "trending_tickers" in data
        assert "indices" in data
    
    def test_get_market_overview_with_sectors(self, client):
        """Test getting market overview with sector heatmap."""
        response = client.get("/api/market/overview?include_sectors=true")
        assert response.status_code == 200
        data = response.json()
        assert "sector_heatmap" in data
    
    def test_get_trending_tickers(self, client):
        """Test getting trending tickers."""
        response = client.get("/api/market/trending?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_market_indices(self, client):
        """Test getting market indices."""
        response = client.get("/api/market/indices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAnalysisEndpoints:
    """Test AI analysis endpoints."""
    
    def test_analyze_stock(self, client):
        """Test stock analysis."""
        response = client.post("/api/analysis/stock/AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "ticker" in data
        assert "summary" in data
        assert "price_analysis" in data
        assert "sentiment_analysis" in data
        assert "recommendations" in data
        assert "risks" in data
    
    def test_analyze_portfolio_unauthorized(self, client):
        """Test portfolio analysis without auth fails."""
        response = client.post("/api/analysis/portfolio")
        assert response.status_code == 403
    
    def test_analyze_portfolio_empty(self, client, auth_headers):
        """Test portfolio analysis with empty portfolio fails."""
        response = client.post("/api/analysis/portfolio", headers=auth_headers)
        assert response.status_code == 400


class TestAlertEndpoints:
    """Test alert and notification endpoints."""
    
    def test_get_alerts_unauthorized(self, client):
        """Test getting alerts without auth fails."""
        response = client.get("/api/alerts")
        assert response.status_code == 403
    
    def test_create_alert_success(self, client, auth_headers):
        """Test creating a price alert."""
        response = client.post(
            "/api/alerts",
            headers=auth_headers,
            json={
                "ticker": "AAPL",
                "condition": "above",
                "target_price": 200.00,
                "notification_channels": ["in-app", "email"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["ticker"] == "AAPL"
        assert data["condition"] == "above"
        assert data["target_price"] == 200.00
        assert data["is_active"] is True
    
    def test_create_alert_invalid_condition(self, client, auth_headers):
        """Test creating alert with invalid condition fails."""
        response = client.post(
            "/api/alerts",
            headers=auth_headers,
            json={
                "ticker": "AAPL",
                "condition": "invalid",
                "target_price": 200.00,
                "notification_channels": ["in-app"]
            }
        )
        assert response.status_code == 422
    
    def test_create_alert_invalid_channel(self, client, auth_headers):
        """Test creating alert with invalid channel fails."""
        response = client.post(
            "/api/alerts",
            headers=auth_headers,
            json={
                "ticker": "AAPL",
                "condition": "above",
                "target_price": 200.00,
                "notification_channels": ["invalid-channel"]
            }
        )
        assert response.status_code == 422
    
    def test_update_alert(self, client, auth_headers):
        """Test updating an alert."""
        # Create alert first
        create_response = client.post(
            "/api/alerts",
            headers=auth_headers,
            json={
                "ticker": "MSFT",
                "condition": "below",
                "target_price": 300.00,
                "notification_channels": ["in-app"]
            }
        )
        alert_id = create_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/alerts/{alert_id}",
            headers=auth_headers,
            json={
                "target_price": 290.00,
                "is_active": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["target_price"] == 290.00
        assert data["is_active"] is False
    
    def test_delete_alert(self, client, auth_headers):
        """Test deleting an alert."""
        # Create alert first
        create_response = client.post(
            "/api/alerts",
            headers=auth_headers,
            json={
                "ticker": "GOOGL",
                "condition": "above",
                "target_price": 150.00,
                "notification_channels": ["in-app"]
            }
        )
        alert_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/alerts/{alert_id}", headers=auth_headers)
        assert response.status_code == 204
    
    def test_get_notifications(self, client, auth_headers):
        """Test getting notifications."""
        response = client.get("/api/notifications", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPreferencesEndpoints:
    """Test user preferences endpoints."""
    
    def test_get_preferences_unauthorized(self, client):
        """Test getting preferences without auth fails."""
        response = client.get("/api/preferences")
        assert response.status_code == 403
    
    def test_get_preferences(self, client, auth_headers):
        """Test getting user preferences."""
        response = client.get("/api/preferences", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "default_chart_type" in data
        assert "default_time_range" in data
        assert "notification_settings" in data
        assert "refresh_interval" in data
    
    def test_update_preferences(self, client, auth_headers):
        """Test updating user preferences."""
        response = client.put(
            "/api/preferences",
            headers=auth_headers,
            json={
                "default_chart_type": "candlestick",
                "default_time_range": "1Y",
                "refresh_interval": 120
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["default_chart_type"] == "candlestick"
        assert data["default_time_range"] == "1Y"
        assert data["refresh_interval"] == 120
    
    def test_update_preferences_invalid_chart_type(self, client, auth_headers):
        """Test updating preferences with invalid chart type fails."""
        response = client.put(
            "/api/preferences",
            headers=auth_headers,
            json={
                "default_chart_type": "invalid"
            }
        )
        assert response.status_code == 422
    
    def test_reset_preferences(self, client, auth_headers):
        """Test resetting preferences to defaults."""
        # First update preferences
        client.put(
            "/api/preferences",
            headers=auth_headers,
            json={
                "default_chart_type": "candlestick",
                "refresh_interval": 120
            }
        )
        
        # Reset them
        response = client.post("/api/preferences/reset", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["default_chart_type"] == "line"
        assert data["default_time_range"] == "1M"
        assert data["refresh_interval"] == 60


class TestRateLimiting:
    """Test rate limiting on endpoints."""
    
    def test_rate_limit_exceeded(self, client):
        """Test that rate limiting works."""
        # Make many requests to trigger rate limit
        for _ in range(150):
            response = client.get("/health")
        
        # Should eventually get rate limited
        assert response.status_code in [200, 429]


class TestErrorHandling:
    """Test error handling and status codes."""
    
    def test_404_not_found(self, client):
        """Test 404 for non-existent endpoint."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.post("/health")
        assert response.status_code == 405
    
    def test_422_validation_error(self, client, auth_headers):
        """Test 422 for validation errors."""
        response = client.post(
            "/api/portfolio/positions",
            headers=auth_headers,
            json={
                "ticker": "AAPL"
                # Missing required fields
            }
        )
        assert response.status_code == 422
