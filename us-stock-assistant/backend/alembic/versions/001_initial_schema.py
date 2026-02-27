"""initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create portfolios table
    op.create_table('portfolios',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create stock_positions table
    op.create_table('stock_positions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.DECIMAL(precision=15, scale=4), nullable=False),
        sa.Column('purchase_price', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_positions_portfolio', 'stock_positions', ['portfolio_id'])
    op.create_index('idx_positions_ticker', 'stock_positions', ['ticker'])

    # Create price_alerts table
    op.create_table('price_alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('condition', sa.String(length=10), nullable=False),
        sa.Column('target_price', sa.DECIMAL(precision=15, scale=2), nullable=False),
        sa.Column('notification_channels', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("condition IN ('above', 'below')", name='price_alerts_condition_check'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_alerts_user', 'price_alerts', ['user_id'])
    op.create_index('idx_alerts_active', 'price_alerts', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('default_chart_type', sa.String(length=20), nullable=True),
        sa.Column('default_time_range', sa.String(length=10), nullable=True),
        sa.Column('preferred_news_sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('refresh_interval', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )

    # Create notifications table
    op.create_table('notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_notifications_user', 'notifications', ['user_id'])
    op.create_index('idx_notifications_unread', 'notifications', ['user_id', 'is_read'], postgresql_where=sa.text('is_read = false'))

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_user', 'audit_log', ['user_id'])
    op.create_index('idx_audit_created', 'audit_log', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_audit_created', table_name='audit_log')
    op.drop_index('idx_audit_user', table_name='audit_log')
    op.drop_table('audit_log')
    
    op.drop_index('idx_notifications_unread', table_name='notifications')
    op.drop_index('idx_notifications_user', table_name='notifications')
    op.drop_table('notifications')
    
    op.drop_table('user_preferences')
    
    op.drop_index('idx_alerts_active', table_name='price_alerts')
    op.drop_index('idx_alerts_user', table_name='price_alerts')
    op.drop_table('price_alerts')
    
    op.drop_index('idx_positions_ticker', table_name='stock_positions')
    op.drop_index('idx_positions_portfolio', table_name='stock_positions')
    op.drop_table('stock_positions')
    
    op.drop_table('portfolios')
    op.drop_table('users')
