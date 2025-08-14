"""add refresh_tokens table

Revision ID: 0003_refresh_tokens
Revises: 0002_expense_indexes
Create Date: 2025-08-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003_refresh_tokens'
down_revision: Union[str, None] = '0002_expense_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # NOTE: We intentionally rely on Column(index=True) for single-column indexes.
    # Creating a second explicit index on token_hash produced a duplicate when running on SQLite.
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('token_hash', sa.String(length=128), nullable=False, index=True),  # single-column index auto-created
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column('revoked', sa.Boolean(), nullable=False, server_default=sa.text('false'), index=True),
        sa.Column('replaced_by', sa.Integer(), nullable=True),
    )
    # Composite covering index for validity queries
    op.create_index('ix_refresh_tokens_user_valid', 'refresh_tokens', ['user_id', 'revoked', 'expires_at'])
    # Removed explicit op.create_index for token_hash to avoid duplicate (already created by Column(index=True))


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_user_valid', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
