from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Date, Boolean, Integer, Text, DECIMAL, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import uuid
from datetime import date
from decimal import Decimal
from app.database import Base
from app.validators import (
    validate_ticker,
    validate_positive_quantity,
    validate_positive_price,
    validate_purchase_date,
    validate_alert_condition,
    validate_notification_channels
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    portfolio = relationship("Portfolio", back_populates="user", uselist=False, cascade="all, delete-orphan")
    price_alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="portfolio")
    positions = relationship("StockPosition", back_populates="portfolio", cascade="all, delete-orphan")


class StockPosition(Base):
    __tablename__ = "stock_positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String(10), nullable=False)
    quantity = Column(DECIMAL(15, 4), nullable=False)
    purchase_price = Column(DECIMAL(15, 2), nullable=False)
    purchase_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    portfolio = relationship("Portfolio", back_populates="positions")
    
    @validates('ticker')
    def validate_ticker_format(self, key, ticker):
        """Validate ticker symbol format."""
        return validate_ticker(ticker)
    
    @validates('quantity')
    def validate_quantity_positive(self, key, quantity):
        """Validate quantity is positive."""
        return validate_positive_quantity(Decimal(str(quantity)))
    
    @validates('purchase_price')
    def validate_price_positive(self, key, price):
        """Validate purchase price is positive."""
        return validate_positive_price(Decimal(str(price)))
    
    @validates('purchase_date')
    def validate_date_not_future(self, key, purchase_date):
        """Validate purchase date is not in the future."""
        return validate_purchase_date(purchase_date)


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticker = Column(String(10), nullable=False)
    condition = Column(String(10), nullable=False)
    target_price = Column(DECIMAL(15, 2), nullable=False)
    notification_channels = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="price_alerts")
    
    @validates('ticker')
    def validate_ticker_format(self, key, ticker):
        """Validate ticker symbol format."""
        return validate_ticker(ticker)
    
    @validates('condition')
    def validate_condition_value(self, key, condition):
        """Validate alert condition."""
        return validate_alert_condition(condition)
    
    @validates('target_price')
    def validate_price_positive(self, key, price):
        """Validate target price is positive."""
        return validate_positive_price(Decimal(str(price)))
    
    @validates('notification_channels')
    def validate_channels(self, key, channels):
        """Validate notification channels."""
        return validate_notification_channels(channels)


class UserPreferences(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    default_chart_type = Column(String(20), default="line")
    default_time_range = Column(String(10), default="1M")
    preferred_news_sources = Column(JSONB, default=[])
    notification_settings = Column(JSONB, nullable=False)
    refresh_interval = Column(Integer, default=60)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="preferences")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(255))
    details = Column(JSONB)
    ip_address = Column(INET)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="audit_logs")


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    workflow_type = Column(String(50), nullable=False)  # price_alert, research, rebalancing
    definition = Column(JSONB, nullable=False)  # Workflow nodes and edges
    execution_mode = Column(String(20), default="sequential")  # sequential or parallel
    schedule = Column(String(100))  # Cron schedule if recurring
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 0-100
    current_node = Column(String(100))
    results = Column(JSONB)
    errors = Column(JSONB)
    execution_time = Column(Integer)  # milliseconds
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workflow = relationship("Workflow", back_populates="executions")


class PolicyAcceptance(Base):
    __tablename__ = "policy_acceptances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    policy_type = Column(String(50), nullable=False)  # 'privacy_policy' or 'terms_of_service'
    policy_version = Column(String(20), nullable=False)
    accepted_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(INET)
    
    __table_args__ = (
        CheckConstraint("policy_type IN ('privacy_policy', 'terms_of_service')", name='check_policy_type'),
    )


class DataDeletionRequest(Base):
    __tablename__ = "data_deletion_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    user_email = Column(String(255), nullable=False)  # Store email in case user is deleted
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_deletion_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, cancelled
    completed_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'completed', 'cancelled')", name='check_deletion_status'),
    )
