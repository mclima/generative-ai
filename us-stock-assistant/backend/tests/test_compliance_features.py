"""
Tests for data privacy and compliance features.
Tests data export, account deletion, and policy acceptance tracking.
"""

import pytest
import bcrypt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import (
    User, Portfolio, StockPosition, PriceAlert,
    UserPreferences, Notification, PolicyAcceptance,
    DataDeletionRequest
)
from app.database import Base, engine
from tests.conftest import test_user, test_db, client, auth_headers


class TestDataExport:
    """Test data export functionality (GDPR/CCPA compliance)."""
    
    def test_export_data_completeness(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test that data export includes all user data."""
        # Get the test user
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        
        # Add some test data
        portfolio = Portfolio(user_id=user.id)
        test_db.add(portfolio)
        test_db.commit()
        
        position = StockPosition(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=10,
            purchase_price=150.00,
            purchase_date=datetime.now().date()
        )
        test_db.add(position)
        
        alert = PriceAlert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=200.00,
            notification_channels=["in-app", "email"]
        )
        test_db.add(alert)
        
        notification = Notification(
            user_id=user.id,
            type="price_alert",
            title="Test Alert",
            message="Test message",
            data={"ticker": "AAPL"}
        )
        test_db.add(notification)
        test_db.commit()
        
        # Export data
        response = client.get("/api/compliance/export-data", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all sections are present
        assert "export_date" in data
        assert "user" in data
        assert "portfolio" in data
        assert "alerts" in data
        assert "preferences" in data
        assert "notifications" in data
        assert "policy_acceptances" in data
        
        # Verify user data
        assert data["user"]["email"] == "test@example.com"
        
        # Verify portfolio data
        assert data["portfolio"] is not None
        assert len(data["portfolio"]["positions"]) == 1
        assert data["portfolio"]["positions"][0]["ticker"] == "AAPL"
        assert data["portfolio"]["positions"][0]["quantity"] == 10.0
        
        # Verify alerts
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["ticker"] == "AAPL"
        assert data["alerts"][0]["target_price"] == 200.00
        
        # Verify notifications
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["title"] == "Test Alert"
    
    def test_export_data_without_portfolio(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test data export for user without portfolio."""
        response = client.get("/api/compliance/export-data", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return structure with null portfolio
        assert data["portfolio"] is None
        assert data["alerts"] == []
        assert data["notifications"] == []
    
    def test_export_data_unauthorized(self, client: TestClient):
        """Test that data export requires authentication."""
        response = client.get("/api/compliance/export-data")
        # Should return 403 (Forbidden) when no authentication is provided
        assert response.status_code == 403


class TestAccountDeletion:
    """Test account deletion functionality."""
    
    def test_request_deletion(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test requesting account deletion."""
        response = client.post("/api/compliance/request-deletion", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "scheduled_deletion_date" in data
        
        # Verify deletion is scheduled for 30 days from now
        scheduled_date = datetime.fromisoformat(data["scheduled_deletion_date"])
        expected_date = datetime.utcnow() + timedelta(days=30)
        
        # Allow 1 minute tolerance
        assert abs((scheduled_date - expected_date).total_seconds()) < 60
        
        # Verify deletion request was created in database
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        deletion_request = test_db.query(DataDeletionRequest).filter(
            DataDeletionRequest.user_id == user.id
        ).first()
        
        assert deletion_request is not None
        assert deletion_request.status == "pending"
        assert deletion_request.user_email == "test@example.com"
    
    def test_request_deletion_duplicate(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test that duplicate deletion requests are handled."""
        # First request
        response1 = client.post("/api/compliance/request-deletion", headers=auth_headers)
        assert response1.status_code == 200
        
        # Second request should return existing request
        response2 = client.post("/api/compliance/request-deletion", headers=auth_headers)
        assert response2.status_code == 200
        
        data = response2.json()
        assert "already exists" in data["message"].lower()
    
    def test_cancel_deletion(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test cancelling account deletion."""
        # First request deletion
        client.post("/api/compliance/request-deletion", headers=auth_headers)
        
        # Then cancel it
        response = client.post("/api/compliance/cancel-deletion", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "cancelled" in data["message"].lower()
        
        # Verify status in database
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        deletion_request = test_db.query(DataDeletionRequest).filter(
            DataDeletionRequest.user_id == user.id
        ).first()
        
        assert deletion_request.status == "cancelled"
    
    def test_cancel_deletion_without_request(self, client: TestClient, auth_headers: dict):
        """Test cancelling deletion when no request exists."""
        response = client.post("/api/compliance/cancel-deletion", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_deletion_status_no_request(self, client: TestClient, auth_headers: dict):
        """Test getting deletion status when no request exists."""
        response = client.get("/api/compliance/deletion-status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_pending_deletion"] is False
    
    def test_get_deletion_status_with_request(self, client: TestClient, auth_headers: dict):
        """Test getting deletion status with pending request."""
        # Request deletion
        client.post("/api/compliance/request-deletion", headers=auth_headers)
        
        # Check status
        response = client.get("/api/compliance/deletion-status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_pending_deletion"] is True
        assert "scheduled_deletion_date" in data
        assert "requested_at" in data


class TestPolicyAcceptance:
    """Test policy acceptance tracking."""
    
    def test_record_privacy_policy_acceptance(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test recording privacy policy acceptance."""
        response = client.post(
            "/api/compliance/policy-acceptance",
            headers=auth_headers,
            params={
                "policy_type": "privacy_policy",
                "policy_version": "1.0"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["policy_type"] == "privacy_policy"
        
        # Verify in database
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        acceptance = test_db.query(PolicyAcceptance).filter(
            PolicyAcceptance.user_id == user.id,
            PolicyAcceptance.policy_type == "privacy_policy"
        ).first()
        
        assert acceptance is not None
        assert acceptance.policy_version == "1.0"
    
    def test_record_terms_acceptance(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test recording terms of service acceptance."""
        response = client.post(
            "/api/compliance/policy-acceptance",
            headers=auth_headers,
            params={
                "policy_type": "terms_of_service",
                "policy_version": "1.0"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["policy_type"] == "terms_of_service"
    
    def test_invalid_policy_type(self, client: TestClient, auth_headers: dict):
        """Test that invalid policy types are rejected."""
        response = client.post(
            "/api/compliance/policy-acceptance",
            headers=auth_headers,
            params={
                "policy_type": "invalid_type",
                "policy_version": "1.0"
            }
        )
        
        assert response.status_code == 400


class TestDataDeletionFlow:
    """Test complete data deletion flow."""
    
    def test_complete_deletion_flow(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test the complete flow: request -> check status -> cancel."""
        # 1. Request deletion
        response = client.post("/api/compliance/request-deletion", headers=auth_headers)
        assert response.status_code == 200
        scheduled_date = response.json()["scheduled_deletion_date"]
        
        # 2. Check status
        response = client.get("/api/compliance/deletion-status", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["has_pending_deletion"] is True
        assert response.json()["scheduled_deletion_date"] == scheduled_date
        
        # 3. Cancel deletion
        response = client.post("/api/compliance/cancel-deletion", headers=auth_headers)
        assert response.status_code == 200
        
        # 4. Verify status updated
        response = client.get("/api/compliance/deletion-status", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["has_pending_deletion"] is False
    
    def test_export_before_deletion(self, client: TestClient, auth_headers: dict, test_db: Session):
        """Test exporting data before requesting deletion."""
        # Add some data
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        portfolio = Portfolio(user_id=user.id)
        test_db.add(portfolio)
        test_db.commit()
        
        # Export data
        export_response = client.get("/api/compliance/export-data", headers=auth_headers)
        assert export_response.status_code == 200
        export_data = export_response.json()
        
        # Request deletion
        delete_response = client.post("/api/compliance/request-deletion", headers=auth_headers)
        assert delete_response.status_code == 200
        
        # Verify data is still accessible
        export_response2 = client.get("/api/compliance/export-data", headers=auth_headers)
        assert export_response2.status_code == 200
        
        # Data should be the same
        assert export_response2.json()["user"]["email"] == export_data["user"]["email"]


class TestComplianceIntegration:
    """Integration tests for compliance features."""
    
    def test_full_user_lifecycle(self, client: TestClient, test_db: Session):
        """Test full user lifecycle with compliance features."""
        # 1. Create a test user
        password = "testpassword123"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            email="test@example.com",
            password_hash=password_hash
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # 2. Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Record policy acceptances
        client.post(
            "/api/compliance/policy-acceptance",
            headers=headers,
            params={"policy_type": "privacy_policy", "policy_version": "1.0"}
        )
        client.post(
            "/api/compliance/policy-acceptance",
            headers=headers,
            params={"policy_type": "terms_of_service", "policy_version": "1.0"}
        )
        
        # 4. Use the application (add portfolio data)
        user = test_db.query(User).filter(User.email == "test@example.com").first()
        portfolio = Portfolio(user_id=user.id)
        test_db.add(portfolio)
        test_db.commit()
        
        # 5. Export data
        export_response = client.get("/api/compliance/export-data", headers=headers)
        assert export_response.status_code == 200
        export_data = export_response.json()
        assert len(export_data["policy_acceptances"]) == 2
        
        # 6. Request deletion
        delete_response = client.post("/api/compliance/request-deletion", headers=headers)
        assert delete_response.status_code == 200
        
        # 7. Verify deletion is scheduled
        status_response = client.get("/api/compliance/deletion-status", headers=headers)
        assert status_response.status_code == 200
        assert status_response.json()["has_pending_deletion"] is True
