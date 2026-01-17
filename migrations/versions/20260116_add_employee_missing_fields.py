"""Add missing employee fields: foreign_name, bank_name, account_number, account_holder

Revision ID: 8g9b0c1d2e3f
Revises: 7f8a9b0c1d2e
Create Date: 2026-01-16 15:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8g9b0c1d2e3f'
down_revision: Union[str, None] = '7f8a9b0c1d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign_name column
    op.add_column('employees', sa.Column('foreign_name', sa.String(100), nullable=True))

    # Add bank info columns
    op.add_column('employees', sa.Column('bank_name', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('account_number', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('account_holder', sa.String(50), nullable=True))


def downgrade() -> None:
    # Remove bank info columns
    op.drop_column('employees', 'account_holder')
    op.drop_column('employees', 'account_number')
    op.drop_column('employees', 'bank_name')

    # Remove foreign_name column
    op.drop_column('employees', 'foreign_name')
