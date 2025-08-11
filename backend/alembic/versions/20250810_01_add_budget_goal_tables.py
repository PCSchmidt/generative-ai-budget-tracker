"""add budget and goal tables

Revision ID: 20250810_01
Revises: 0003_refresh_tokens
Create Date: 2025-08-10
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250810_01'
down_revision = '0003_refresh_tokens'  # chained to last applied migration
branch_labels = None
depends_on = None


def upgrade():
    # goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(length=150), nullable=False, index=True),
        sa.Column('target_amount', sa.Float(), nullable=False),
        sa.Column('current_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('target_date', sa.Date(), nullable=True, index=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_goals_user_name', 'goals', ['user_id', 'name'])  # assist duplicate name checks per user

    # budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('period', sa.String(length=20), nullable=False),  # e.g. 2025-08
        sa.Column('total_limit', sa.Float(), nullable=False),
        sa.Column('spent_amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('notes', sa.Text(), nullable=True),
    )
    op.create_index('ix_budgets_period', 'budgets', ['period'])
    op.create_index('ix_budgets_user_period', 'budgets', ['user_id', 'period'], unique=True)


def downgrade():
    op.drop_index('ix_budgets_user_period', table_name='budgets')
    op.drop_index('ix_budgets_period', table_name='budgets')
    op.drop_table('budgets')
    op.drop_index('ix_goals_user_name', table_name='goals')
    op.drop_table('goals')
