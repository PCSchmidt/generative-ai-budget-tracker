"""add optimized expense indexes

Revision ID: 0002_expense_indexes
Revises: 0001_initial
Create Date: 2025-08-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0002_expense_indexes'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

"""
Rationale:
Previous migration created single-column indexes on expenses.user_id and expenses.category.
Common query patterns we anticipate:
 1. Recent expenses for a user ordered by date: WHERE user_id = ? ORDER BY expense_date DESC LIMIT N
 2. Aggregations by category per user: WHERE user_id = ? GROUP BY category
Composite indexes (user_id, expense_date DESC) and (user_id, category) support these efficiently and cover
both filtering and ordering/grouping. The standalone category index offered little selectivity without user_id
and is replaced. Standalone user_id index becomes redundant once (user_id, expense_date) and (user_id, category)
exist; most ORMs can still use the leading column of a composite index for pure user_id filters if needed.
"""

def upgrade() -> None:
    # Create new composite indexes
    op.create_index('ix_expenses_user_date', 'expenses', ['user_id', sa.text('expense_date DESC')])
    op.create_index('ix_expenses_user_category', 'expenses', ['user_id', 'category'])

    # Drop older, less optimal indexes if they exist (names from 0001_initial)
    # Use try/except pattern is not available directly; assuming they exist as we control prior migration.
    op.drop_index('ix_expenses_user_id', table_name='expenses')
    op.drop_index('ix_expenses_category', table_name='expenses')


def downgrade() -> None:
    # Recreate old single-column indexes
    op.create_index('ix_expenses_user_id', 'expenses', ['user_id'])
    op.create_index('ix_expenses_category', 'expenses', ['category'])

    # Drop new composite indexes
    op.drop_index('ix_expenses_user_category', table_name='expenses')
    op.drop_index('ix_expenses_user_date', table_name='expenses')
