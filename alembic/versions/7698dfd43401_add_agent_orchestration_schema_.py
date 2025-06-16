"""Add agent orchestration schema enhancements

Revision ID: 7698dfd43401
Revises: 
Create Date: 2025-06-13 17:15:30.051216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7698dfd43401'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add agent orchestration capabilities."""
    
    # Create tools table with comprehensive tool definitions
    op.create_table('tools',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('tool_name', sa.String(255), nullable=False),
        sa.Column('tool_description', sa.Text(), nullable=False),
        sa.Column('input_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('output_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('example_calls', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_handling', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tool_version', sa.String(50), nullable=True, server_default='1.0.0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('deprecation_date', sa.DateTime(), nullable=True),
        sa.Column('deprecation_notice', sa.Text(), nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rate_limit_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('service_id', 'tool_name', name='uq_service_tool_name')
    )
    
    # Create indexes for tools table
    op.create_index('idx_tools_service_id', 'tools', ['service_id'])
    op.create_index('idx_tools_name', 'tools', ['tool_name'])
    op.create_index('idx_tools_active', 'tools', ['is_active'])
    op.create_index('idx_tools_updated', 'tools', ['updated_at'])
    
    # Create invocation_logs table for tracking actual tool calls
    op.create_table('invocation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('initiator_agent', sa.String(255), nullable=False),
        sa.Column('target_service_id', sa.Integer(), nullable=False),
        sa.Column('target_agent', sa.String(255), nullable=False),
        sa.Column('tool_id', sa.Integer(), nullable=False),
        sa.Column('tool_called', sa.String(255), nullable=False),
        sa.Column('input_parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('success_status', sa.Boolean(), nullable=False),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('invocation_start', sa.DateTime(), nullable=False),
        sa.Column('invocation_end', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('trace_id', sa.String(255), nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['target_service_id'], ['services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create indexes for invocation_logs table
    op.create_index('idx_invocation_logs_initiator', 'invocation_logs', ['initiator_agent'])
    op.create_index('idx_invocation_logs_target', 'invocation_logs', ['target_agent'])
    op.create_index('idx_invocation_logs_tool', 'invocation_logs', ['tool_id'])
    op.create_index('idx_invocation_logs_success', 'invocation_logs', ['success_status'])
    op.create_index('idx_invocation_logs_created', 'invocation_logs', ['created_at'])
    op.create_index('idx_invocation_logs_response_time', 'invocation_logs', ['response_time_ms'])
    op.create_index('idx_invocation_logs_trace', 'invocation_logs', ['trace_id'])
    
    # Add agent orchestration columns to existing services table
    op.add_column('services', sa.Column('agent_protocol', sa.String(50), nullable=True, server_default='kpath-v1'))
    op.add_column('services', sa.Column('auth_type', sa.String(50), nullable=True, server_default='bearer_token'))
    op.add_column('services', sa.Column('auth_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('services', sa.Column('tool_recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('services', sa.Column('agent_capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('services', sa.Column('communication_patterns', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('services', sa.Column('orchestration_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Create indexes for new services columns
    op.create_index('idx_services_agent_protocol', 'services', ['agent_protocol'])
    op.create_index('idx_services_auth_type', 'services', ['auth_type'])
    
    # Add check constraints for agent orchestration fields
    op.create_check_constraint(
        'check_agent_protocol',
        'services',
        "agent_protocol IN ('kpath-v1', 'kpath-v2', 'mcp-v1', 'custom')"
    )
    
    op.create_check_constraint(
        'check_auth_type',
        'services',
        "auth_type IN ('bearer_token', 'api_key', 'oauth2', 'basic_auth', 'custom', 'none')"
    )


def downgrade() -> None:
    """Downgrade schema - Remove agent orchestration capabilities."""
    
    # Remove added columns from services table
    op.drop_column('services', 'orchestration_metadata')
    op.drop_column('services', 'communication_patterns')
    op.drop_column('services', 'agent_capabilities')
    op.drop_column('services', 'tool_recommendations')
    op.drop_column('services', 'auth_config')
    op.drop_column('services', 'auth_type')
    op.drop_column('services', 'agent_protocol')
    
    # Drop indexes for services
    op.drop_index('idx_services_auth_type', table_name='services')
    op.drop_index('idx_services_agent_protocol', table_name='services')
    
    # Drop invocation_logs table
    op.drop_index('idx_invocation_logs_trace', table_name='invocation_logs')
    op.drop_index('idx_invocation_logs_response_time', table_name='invocation_logs')
    op.drop_index('idx_invocation_logs_created', table_name='invocation_logs')
    op.drop_index('idx_invocation_logs_success', table_name='invocation_logs')
    op.drop_index('idx_invocation_logs_tool', table_name='invocation_logs')
    op.drop_index('idx_invocation_logs_target', table_name='invocation_logs')
    op.drop_index('idx_invocation_logs_initiator', table_name='invocation_logs')
    op.drop_table('invocation_logs')
    
    # Drop tools table
    op.drop_index('idx_tools_updated', table_name='tools')
    op.drop_index('idx_tools_active', table_name='tools')
    op.drop_index('idx_tools_name', table_name='tools')
    op.drop_index('idx_tools_service_id', table_name='tools')
    op.drop_table('tools')
