"""add_workflow_tables

Revision ID: e99f29ec6c08
Revises: 001
Create Date: 2026-02-19 21:55:15.340211

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision = 'e99f29ec6c08'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('workflow_type', sa.String(50), nullable=False),
        sa.Column('definition', JSONB, nullable=False),
        sa.Column('execution_mode', sa.String(20), server_default='sequential'),
        sa.Column('schedule', sa.String(100)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create workflow_executions table
    op.create_table(
        'workflow_executions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', UUID(as_uuid=True), sa.ForeignKey('workflows.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('progress', sa.Integer, server_default='0'),
        sa.Column('current_node', sa.String(100)),
        sa.Column('results', JSONB),
        sa.Column('errors', JSONB),
        sa.Column('execution_time', sa.Integer),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create indexes
    op.create_index('idx_workflows_user', 'workflows', ['user_id'])
    op.create_index('idx_workflows_active', 'workflows', ['is_active'])
    op.create_index('idx_executions_workflow', 'workflow_executions', ['workflow_id'])
    op.create_index('idx_executions_status', 'workflow_executions', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_executions_status', 'workflow_executions')
    op.drop_index('idx_executions_workflow', 'workflow_executions')
    op.drop_index('idx_workflows_active', 'workflows')
    op.drop_index('idx_workflows_user', 'workflows')
    
    # Drop tables
    op.drop_table('workflow_executions')
    op.drop_table('workflows')
