"""
Alert Service for managing price alerts and notifications.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging
import asyncio

from app.models import PriceAlert, Notification, User

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing price alerts and notifications."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_price_alert(
        self,
        user_id: UUID,
        ticker: str,
        condition: str,
        target_price: float,
        notification_channels: List[str]
    ) -> PriceAlert:
        """
        Create a new price alert.
        
        Args:
            user_id: UUID of the user
            ticker: Stock ticker symbol
            condition: "above" or "below"
            target_price: Target price threshold
            notification_channels: List of channels (in-app, email, push)
            
        Returns:
            Created PriceAlert object
        """
        alert = PriceAlert(
            user_id=user_id,
            ticker=ticker.upper(),
            condition=condition,
            target_price=target_price,
            notification_channels=notification_channels,
            is_active=True
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_user_alerts(self, user_id: UUID) -> List[PriceAlert]:
        """
        Get all alerts for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of PriceAlert objects
        """
        return self.db.query(PriceAlert).filter(
            PriceAlert.user_id == user_id
        ).all()
    
    def get_active_alerts(self) -> List[PriceAlert]:
        """
        Get all active alerts across all users.
        
        Returns:
            List of active PriceAlert objects
        """
        return self.db.query(PriceAlert).filter(
            PriceAlert.is_active == True
        ).all()
    
    def update_alert(
        self,
        user_id: UUID,
        alert_id: UUID,
        **updates
    ) -> PriceAlert:
        """
        Update an existing alert.
        
        Args:
            user_id: UUID of the user
            alert_id: UUID of the alert
            **updates: Fields to update
            
        Returns:
            Updated PriceAlert object
        """
        alert = self.db.query(PriceAlert).filter(
            and_(
                PriceAlert.id == alert_id,
                PriceAlert.user_id == user_id
            )
        ).first()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found for user {user_id}")
        
        for key, value in updates.items():
            if hasattr(alert, key):
                setattr(alert, key, value)
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def delete_alert(self, user_id: UUID, alert_id: UUID) -> None:
        """
        Delete an alert.
        
        Args:
            user_id: UUID of the user
            alert_id: UUID of the alert
        """
        alert = self.db.query(PriceAlert).filter(
            and_(
                PriceAlert.id == alert_id,
                PriceAlert.user_id == user_id
            )
        ).first()
        
        if not alert:
            raise ValueError(f"Alert {alert_id} not found for user {user_id}")
        
        self.db.delete(alert)
        self.db.commit()
    
    def check_alert_condition(
        self,
        alert: PriceAlert,
        current_price: float
    ) -> bool:
        """
        Check if an alert condition is met.
        
        Args:
            alert: PriceAlert object
            current_price: Current stock price
            
        Returns:
            True if condition is met, False otherwise
        """
        if alert.condition == "above":
            return current_price >= float(alert.target_price)
        elif alert.condition == "below":
            return current_price <= float(alert.target_price)
        return False
    
    def trigger_alert(
        self,
        alert: PriceAlert,
        current_price: float
    ) -> Dict[str, Any]:
        """
        Trigger an alert and create notifications.
        
        Args:
            alert: PriceAlert object
            current_price: Current stock price
            
        Returns:
            Dictionary with trigger details
        """
        # Mark alert as triggered
        alert.triggered_at = datetime.utcnow()
        alert.is_active = False
        
        # Check if notification should be sent (prevent alert fatigue)
        should_send = self.should_send_notification(
            user_id=alert.user_id,
            notification_type="price_alert",
            max_per_window=5,
            time_window_minutes=15
        )
        
        if should_send:
            # Create notification with multiple channels
            title = f"Price Alert: {alert.ticker}"
            message = (
                f"{alert.ticker} is now {alert.condition} ${alert.target_price}. "
                f"Current price: ${current_price:.2f}"
            )
            data = {
                "alert_id": str(alert.id),
                "ticker": alert.ticker,
                "condition": alert.condition,
                "target_price": float(alert.target_price),
                "current_price": current_price,
                "triggered_at": alert.triggered_at.isoformat()
            }
            
            self.send_notification(
                user_id=alert.user_id,
                notification_type="price_alert",
                title=title,
                message=message,
                data=data,
                channels=alert.notification_channels
            )
        else:
            logger.info(
                f"Alert {alert.id} triggered but notification suppressed due to grouping rules"
            )
        
        self.db.commit()
        
        return {
            "alert_id": str(alert.id),
            "ticker": alert.ticker,
            "current_price": current_price,
            "triggered_at": alert.triggered_at.isoformat(),
            "notification_channels": alert.notification_channels,
            "notification_sent": should_send
        }
    
    def send_notification(
        self,
        user_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None
    ) -> Notification:
        """
        Send a notification to a user via multiple channels.
        
        Args:
            user_id: UUID of the user
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            data: Optional additional data
            channels: List of channels to send to (in-app, email, push)
            
        Returns:
            Created Notification object
        """
        # Create in-app notification (always created)
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Send to additional channels if specified
        if channels:
            if "email" in channels:
                self._send_email_notification(user_id, title, message, data)
            if "push" in channels:
                self._send_push_notification(user_id, title, message, data)
        
        # Send real-time WebSocket notification
        self._send_websocket_notification(user_id, notification)
        
        logger.info(f"Notification sent to user {user_id} via channels: {channels or ['in-app']}")
        
        return notification
    
    def _send_email_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Send email notification.
        
        In production, this would integrate with SendGrid or AWS SES.
        For now, this is a placeholder that logs the email.
        
        Args:
            user_id: UUID of the user
            title: Email subject
            message: Email body
            data: Optional additional data
        """
        # Get user email
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found for email notification")
            return
        
        # TODO: Integrate with SendGrid or AWS SES
        # For now, just log the email
        logger.info(f"EMAIL to {user.email}: {title} - {message}")
        
        # Example SendGrid integration (commented out):
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # 
        # message = Mail(
        #     from_email='noreply@stockassistant.com',
        #     to_emails=user.email,
        #     subject=title,
        #     html_content=message
        # )
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        # response = sg.send(message)
    
    def _send_push_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Send push notification.
        
        In production, this would integrate with Firebase Cloud Messaging or similar.
        For now, this is a placeholder that logs the notification.
        
        Args:
            user_id: UUID of the user
            title: Notification title
            message: Notification message
            data: Optional additional data
        """
        # TODO: Integrate with Firebase Cloud Messaging or similar
        # For now, just log the push notification
        logger.info(f"PUSH to user {user_id}: {title} - {message}")
        
        # Example FCM integration (commented out):
        # from firebase_admin import messaging
        # 
        # message = messaging.Message(
        #     notification=messaging.Notification(
        #         title=title,
        #         body=message,
        #     ),
        #     data=data or {},
        #     token=user_device_token,
        # )
        # response = messaging.send(message)
    
    def _send_websocket_notification(
        self,
        user_id: UUID,
        notification: Notification
    ) -> None:
        """
        Send real-time notification via WebSocket.
        
        Args:
            user_id: UUID of the user
            notification: Notification object to send
        """
        try:
            # Import here to avoid circular dependency
            from app.services.websocket_service import get_websocket_service
            
            ws_service = get_websocket_service()
            
            # Prepare notification data
            notification_data = {
                "id": str(notification.id),
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "data": notification.data,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat()
            }
            
            # Send via WebSocket (non-blocking)
            # We need to run this in the event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule the coroutine
                    asyncio.create_task(
                        ws_service.sendNotificationToUser(user_id, notification_data)
                    )
                else:
                    # If no loop is running, run it synchronously
                    loop.run_until_complete(
                        ws_service.sendNotificationToUser(user_id, notification_data)
                    )
            except RuntimeError:
                # No event loop, create a new one
                asyncio.run(
                    ws_service.sendNotificationToUser(user_id, notification_data)
                )
            
            logger.debug(f"WebSocket notification sent to user {user_id}")
        
        except Exception as e:
            # Don't fail the notification if WebSocket fails
            logger.warning(f"Failed to send WebSocket notification to user {user_id}: {e}")
    
    def check_alerts(self, tickers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Check alerts and trigger notifications for price conditions.
        
        This method is called by the Price Alert Agent to monitor alerts.
        
        Args:
            tickers: Optional list of tickers to check. If None, checks all active alerts.
            
        Returns:
            List of triggered alert details
        """
        # Get active alerts
        query = self.db.query(PriceAlert).filter(PriceAlert.is_active == True)
        
        if tickers:
            query = query.filter(PriceAlert.ticker.in_(tickers))
        
        active_alerts = query.all()
        
        logger.info(f"Checking {len(active_alerts)} active alerts")
        
        return [
            {
                "alert_id": str(alert.id),
                "ticker": alert.ticker,
                "condition": alert.condition,
                "target_price": float(alert.target_price),
                "user_id": str(alert.user_id)
            }
            for alert in active_alerts
        ]
    
    def get_notification_history(
        self,
        user_id: UUID,
        notification_type: Optional[str] = None,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get notification history for a user.
        
        Args:
            user_id: UUID of the user
            notification_type: Optional filter by notification type
            limit: Maximum number of notifications to return
            unread_only: If True, return only unread notifications
            
        Returns:
            List of Notification objects
        """
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if notification_type:
            query = query.filter(Notification.type == notification_type)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_notification_read(self, user_id: UUID, notification_id: UUID) -> Notification:
        """
        Mark a notification as read.
        
        Args:
            user_id: UUID of the user
            notification_id: UUID of the notification
            
        Returns:
            Updated Notification object
        """
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if not notification:
            raise ValueError(f"Notification {notification_id} not found for user {user_id}")
        
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def group_notifications(
        self,
        user_id: UUID,
        time_window_minutes: int = 15
    ) -> Dict[str, List[Notification]]:
        """
        Group notifications to prevent alert fatigue.
        
        Groups notifications by type within a time window to avoid
        overwhelming users with too many similar notifications.
        
        Args:
            user_id: UUID of the user
            time_window_minutes: Time window in minutes for grouping
            
        Returns:
            Dictionary mapping notification types to lists of notifications
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        recent_notifications = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.created_at >= cutoff_time,
                Notification.is_read == False
            )
        ).order_by(Notification.created_at.desc()).all()
        
        # Group by type
        grouped = {}
        for notification in recent_notifications:
            if notification.type not in grouped:
                grouped[notification.type] = []
            grouped[notification.type].append(notification)
        
        return grouped
    
    def should_send_notification(
        self,
        user_id: UUID,
        notification_type: str,
        max_per_window: int = 5,
        time_window_minutes: int = 15
    ) -> bool:
        """
        Check if a notification should be sent based on grouping rules.
        
        Prevents alert fatigue by limiting the number of notifications
        of the same type within a time window.
        
        Args:
            user_id: UUID of the user
            notification_type: Type of notification
            max_per_window: Maximum notifications of this type per window
            time_window_minutes: Time window in minutes
            
        Returns:
            True if notification should be sent, False otherwise
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        count = self.db.query(func.count(Notification.id)).filter(
            and_(
                Notification.user_id == user_id,
                Notification.type == notification_type,
                Notification.created_at >= cutoff_time
            )
        ).scalar()
        
        should_send = count < max_per_window
        
        if not should_send:
            logger.info(
                f"Notification suppressed for user {user_id}: "
                f"{count} {notification_type} notifications in last {time_window_minutes} minutes"
            )
        
        return should_send
