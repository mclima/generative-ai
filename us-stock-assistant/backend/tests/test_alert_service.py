"""
Unit tests for Alert Service.

Tests alert creation, updates, deletion, notification delivery,
and notification grouping logic.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal

from app.models import User, PriceAlert, Notification
from app.services.alert_service import AlertService


class TestAlertService:
    """Unit tests for AlertService."""
    
    def test_create_price_alert(self, db_session):
        """Test creating a price alert."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app", "email"]
        )
        
        # Verify alert
        assert alert.id is not None
        assert alert.user_id == user.id
        assert alert.ticker == "AAPL"
        assert alert.condition == "above"
        assert float(alert.target_price) == 150.00
        assert alert.notification_channels == ["in-app", "email"]
        assert alert.is_active is True
        assert alert.triggered_at is None
    
    def test_get_user_alerts(self, db_session):
        """Test retrieving user alerts."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create multiple alerts
        alert1 = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        alert2 = alert_service.create_price_alert(
            user_id=user.id,
            ticker="GOOGL",
            condition="below",
            target_price=100.00,
            notification_channels=["email"]
        )
        
        # Get user alerts
        alerts = alert_service.get_user_alerts(user.id)
        
        # Verify
        assert len(alerts) == 2
        assert any(a.ticker == "AAPL" for a in alerts)
        assert any(a.ticker == "GOOGL" for a in alerts)
    
    def test_update_alert(self, db_session):
        """Test updating an alert."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        # Update alert
        updated_alert = alert_service.update_alert(
            user_id=user.id,
            alert_id=alert.id,
            target_price=160.00,
            notification_channels=["in-app", "email", "push"]
        )
        
        # Verify
        assert float(updated_alert.target_price) == 160.00
        assert updated_alert.notification_channels == ["in-app", "email", "push"]
        assert updated_alert.ticker == "AAPL"  # Unchanged
        assert updated_alert.condition == "above"  # Unchanged
    
    def test_update_alert_not_found(self, db_session):
        """Test updating a non-existent alert."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Try to update non-existent alert
        with pytest.raises(ValueError, match="not found"):
            alert_service.update_alert(
                user_id=user.id,
                alert_id=uuid4(),
                target_price=160.00
            )
    
    def test_delete_alert(self, db_session):
        """Test deleting an alert."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        # Delete alert
        alert_service.delete_alert(user.id, alert.id)
        
        # Verify deletion
        alerts = alert_service.get_user_alerts(user.id)
        assert len(alerts) == 0
    
    def test_delete_alert_not_found(self, db_session):
        """Test deleting a non-existent alert."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Try to delete non-existent alert
        with pytest.raises(ValueError, match="not found"):
            alert_service.delete_alert(user.id, uuid4())
    
    def test_check_alert_condition_above(self, db_session):
        """Test checking alert condition for 'above' threshold."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        # Test condition
        assert alert_service.check_alert_condition(alert, 160.00) is True
        assert alert_service.check_alert_condition(alert, 150.00) is True
        assert alert_service.check_alert_condition(alert, 140.00) is False
    
    def test_check_alert_condition_below(self, db_session):
        """Test checking alert condition for 'below' threshold."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="below",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        # Test condition
        assert alert_service.check_alert_condition(alert, 140.00) is True
        assert alert_service.check_alert_condition(alert, 150.00) is True
        assert alert_service.check_alert_condition(alert, 160.00) is False
    
    def test_trigger_alert(self, db_session):
        """Test triggering an alert."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alert
        alert = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app", "email"]
        )
        
        # Trigger alert
        result = alert_service.trigger_alert(alert, 160.00)
        
        # Verify result
        assert result["alert_id"] == str(alert.id)
        assert result["ticker"] == "AAPL"
        assert result["current_price"] == 160.00
        assert "triggered_at" in result
        assert result["notification_channels"] == ["in-app", "email"]
        
        # Verify alert is now inactive
        db_session.refresh(alert)
        assert alert.is_active is False
        assert alert.triggered_at is not None
        
        # Verify notification was created
        notifications = db_session.query(Notification).filter(
            Notification.user_id == user.id
        ).all()
        assert len(notifications) == 1
        assert notifications[0].type == "price_alert"
        assert "AAPL" in notifications[0].title
    
    def test_send_notification_in_app(self, db_session):
        """Test sending in-app notification."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Send notification
        notification = alert_service.send_notification(
            user_id=user.id,
            notification_type="test",
            title="Test Notification",
            message="This is a test",
            data={"key": "value"},
            channels=["in-app"]
        )
        
        # Verify
        assert notification.id is not None
        assert notification.user_id == user.id
        assert notification.type == "test"
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test"
        assert notification.data == {"key": "value"}
        assert notification.is_read is False
    
    def test_send_notification_multiple_channels(self, db_session):
        """Test sending notification to multiple channels."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Send notification (should not raise error)
        notification = alert_service.send_notification(
            user_id=user.id,
            notification_type="test",
            title="Test Notification",
            message="This is a test",
            channels=["in-app", "email", "push"]
        )
        
        # Verify in-app notification was created
        assert notification.id is not None
    
    def test_check_alerts(self, db_session):
        """Test checking all active alerts."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alerts
        alert1 = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        alert2 = alert_service.create_price_alert(
            user_id=user.id,
            ticker="GOOGL",
            condition="below",
            target_price=100.00,
            notification_channels=["email"]
        )
        
        # Check alerts
        alerts = alert_service.check_alerts()
        
        # Verify
        assert len(alerts) == 2
        assert any(a["ticker"] == "AAPL" for a in alerts)
        assert any(a["ticker"] == "GOOGL" for a in alerts)
    
    def test_check_alerts_filtered_by_ticker(self, db_session):
        """Test checking alerts filtered by ticker."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create alerts
        alert1 = alert_service.create_price_alert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=150.00,
            notification_channels=["in-app"]
        )
        
        alert2 = alert_service.create_price_alert(
            user_id=user.id,
            ticker="GOOGL",
            condition="below",
            target_price=100.00,
            notification_channels=["email"]
        )
        
        # Check alerts for specific ticker
        alerts = alert_service.check_alerts(tickers=["AAPL"])
        
        # Verify
        assert len(alerts) == 1
        assert alerts[0]["ticker"] == "AAPL"
    
    def test_get_notification_history(self, db_session):
        """Test getting notification history."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create notifications
        alert_service.send_notification(
            user_id=user.id,
            notification_type="price_alert",
            title="Alert 1",
            message="Message 1"
        )
        
        alert_service.send_notification(
            user_id=user.id,
            notification_type="news_update",
            title="News 1",
            message="News message"
        )
        
        # Get all notifications
        notifications = alert_service.get_notification_history(user.id)
        assert len(notifications) == 2
        
        # Get filtered notifications
        price_alerts = alert_service.get_notification_history(
            user.id,
            notification_type="price_alert"
        )
        assert len(price_alerts) == 1
        assert price_alerts[0].type == "price_alert"
    
    def test_mark_notification_read(self, db_session):
        """Test marking notification as read."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create notification
        notification = alert_service.send_notification(
            user_id=user.id,
            notification_type="test",
            title="Test",
            message="Test message"
        )
        
        # Verify initially unread
        assert notification.is_read is False
        
        # Mark as read
        updated = alert_service.mark_notification_read(user.id, notification.id)
        
        # Verify
        assert updated.is_read is True
    
    def test_group_notifications(self, db_session):
        """Test grouping notifications by type."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create notifications of different types
        alert_service.send_notification(
            user_id=user.id,
            notification_type="price_alert",
            title="Alert 1",
            message="Message 1"
        )
        
        alert_service.send_notification(
            user_id=user.id,
            notification_type="price_alert",
            title="Alert 2",
            message="Message 2"
        )
        
        alert_service.send_notification(
            user_id=user.id,
            notification_type="news_update",
            title="News 1",
            message="News message"
        )
        
        # Group notifications
        grouped = alert_service.group_notifications(user.id, time_window_minutes=60)
        
        # Verify grouping
        assert "price_alert" in grouped
        assert "news_update" in grouped
        assert len(grouped["price_alert"]) == 2
        assert len(grouped["news_update"]) == 1
    
    def test_should_send_notification_within_limit(self, db_session):
        """Test notification sending is allowed within limit."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create a few notifications
        for i in range(3):
            alert_service.send_notification(
                user_id=user.id,
                notification_type="price_alert",
                title=f"Alert {i}",
                message=f"Message {i}"
            )
        
        # Should still allow more notifications
        should_send = alert_service.should_send_notification(
            user_id=user.id,
            notification_type="price_alert",
            max_per_window=5,
            time_window_minutes=15
        )
        
        assert should_send is True
    
    def test_should_send_notification_exceeds_limit(self, db_session):
        """Test notification sending is blocked when limit exceeded."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create max notifications
        for i in range(5):
            alert_service.send_notification(
                user_id=user.id,
                notification_type="price_alert",
                title=f"Alert {i}",
                message=f"Message {i}"
            )
        
        # Should block more notifications
        should_send = alert_service.should_send_notification(
            user_id=user.id,
            notification_type="price_alert",
            max_per_window=5,
            time_window_minutes=15
        )
        
        assert should_send is False
    
    def test_should_send_notification_different_types(self, db_session):
        """Test notification limits are per type."""
        # Create user
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create alert service
        alert_service = AlertService(db_session)
        
        # Create max price_alert notifications
        for i in range(5):
            alert_service.send_notification(
                user_id=user.id,
                notification_type="price_alert",
                title=f"Alert {i}",
                message=f"Message {i}"
            )
        
        # Should still allow news_update notifications
        should_send = alert_service.should_send_notification(
            user_id=user.id,
            notification_type="news_update",
            max_per_window=5,
            time_window_minutes=15
        )
        
        assert should_send is True
