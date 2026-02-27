"""
Property-based tests for Price Alert Agent.

Feature: us-stock-assistant, Property 20: Price Alert Triggering
**Validates: Requirements 5.1**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

from app.models import User, PriceAlert, Notification
from app.services.agents.price_alert_agent import PriceAlertAgent
from app.services.alert_service import AlertService
from app.services.stock_data_service import StockDataService


# Strategies for generating test data
@st.composite
def price_alert_data(draw):
    """Generate valid price alert data."""
    ticker = draw(st.sampled_from(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]))
    condition = draw(st.sampled_from(["above", "below"]))
    target_price = draw(st.floats(min_value=1.0, max_value=1000.0))
    current_price = draw(st.floats(min_value=1.0, max_value=1000.0))
    
    return {
        "ticker": ticker,
        "condition": condition,
        "target_price": round(target_price, 2),
        "current_price": round(current_price, 2),
        "notification_channels": ["in-app"]
    }


class TestPriceAlertAgentProperties:
    """Property-based tests for Price Alert Agent."""
    
    @given(alert_data=price_alert_data())
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_20_price_alert_triggering(self, db_session, alert_data):
        """
        Property 20: Price Alert Triggering
        
        For any active price alert, when the stock price crosses the target threshold
        (above or below), the agentic system should trigger a notification to the user
        via configured channels.
        
        **Validates: Requirements 5.1**
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create price alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker=alert_data["ticker"],
            condition=alert_data["condition"],
            target_price=alert_data["target_price"],
            notification_channels=alert_data["notification_channels"]
        )
        
        # Verify alert is active
        assert alert.is_active is True
        
        # Check if condition should be met
        current_price = alert_data["current_price"]
        target_price = alert_data["target_price"]
        condition = alert_data["condition"]
        
        should_trigger = (
            (condition == "above" and current_price >= target_price) or
            (condition == "below" and current_price <= target_price)
        )
        
        # Check alert condition
        condition_met = alert_service.check_alert_condition(alert, current_price)
        
        # Verify condition check matches expected result
        assert condition_met == should_trigger
        
        if should_trigger:
            # Trigger the alert
            trigger_result = alert_service.trigger_alert(alert, current_price)
            
            # Verify alert was triggered
            assert trigger_result["ticker"] == alert_data["ticker"]
            assert trigger_result["current_price"] == current_price
            assert "triggered_at" in trigger_result
            
            # Verify alert is now inactive
            db_session.refresh(alert)
            assert alert.is_active is False
            assert alert.triggered_at is not None
            
            # Verify notification was created
            notifications = db_session.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.type == "price_alert"
            ).all()
            
            assert len(notifications) >= 1
            notification = notifications[-1]  # Get the most recent
            
            # Verify notification content
            assert alert_data["ticker"] in notification.title
            assert notification.data["ticker"] == alert_data["ticker"]
            assert notification.data["condition"] == condition
            assert notification.data["target_price"] == target_price
            assert notification.data["current_price"] == current_price
            assert notification.data["alert_id"] == str(alert.id)
    
    @given(
        ticker=st.sampled_from(["AAPL", "GOOGL", "MSFT"]),
        num_alerts=st.integers(min_value=1, max_value=5)
    )
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_multiple_alerts_same_ticker(self, db_session, ticker, num_alerts):
        """
        Test that multiple alerts for the same ticker are handled correctly.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        alert_service = AlertService(db_session)
        
        # Create multiple alerts with different target prices
        alerts = []
        for i in range(num_alerts):
            alert = alert_service.create_price_alert(
                user_id=user.id,
                ticker=ticker,
                condition="above" if i % 2 == 0 else "below",
                target_price=100.0 + (i * 10.0),
                notification_channels=["in-app"]
            )
            alerts.append(alert)
        
        # Verify all alerts were created
        assert len(alerts) == num_alerts
        
        # Verify all alerts are active
        for alert in alerts:
            assert alert.is_active is True
            assert alert.ticker == ticker
    
    @given(
        condition=st.sampled_from(["above", "below"]),
        target_price=st.floats(min_value=50.0, max_value=200.0),
        price_offset=st.floats(min_value=-50.0, max_value=50.0)
    )
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_alert_condition_logic(self, db_session, condition, target_price, price_offset):
        """
        Test that alert condition logic is correct for all price combinations.
        """
        target_price = round(target_price, 2)
        current_price = round(target_price + price_offset, 2)
        
        # Skip if prices are invalid
        assume(current_price > 0)
        
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="TEST",
            condition=condition,
            target_price=target_price,
            notification_channels=["in-app"]
        )
        
        # Check condition
        condition_met = alert_service.check_alert_condition(alert, current_price)
        
        # Verify logic
        if condition == "above":
            assert condition_met == (current_price >= target_price)
        else:  # below
            assert condition_met == (current_price <= target_price)
    
    @given(
        channels=st.lists(
            st.sampled_from(["in-app", "email", "push"]),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_notification_channels_preserved(self, db_session, channels):
        """
        Test that notification channels are preserved when alert is triggered.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="TEST",
            condition="above",
            target_price=100.0,
            notification_channels=channels
        )
        
        # Verify channels are stored
        assert set(alert.notification_channels) == set(channels)
        
        # Trigger alert
        trigger_result = alert_service.trigger_alert(alert, 150.0)
        
        # Verify channels are in trigger result
        assert set(trigger_result["notification_channels"]) == set(channels)
