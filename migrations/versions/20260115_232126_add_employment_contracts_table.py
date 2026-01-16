"""add employment_contracts table

Revision ID: 42bb3326914c
Revises: 5bf4a06d5f9c
Create Date: 2026-01-15 23:21:26.718404+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42bb3326914c'
down_revision: Union[str, None] = '5bf4a06d5f9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # employment_contracts 테이블 생성
    op.create_table('employment_contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('contract_date', sa.Date(), nullable=True),
        sa.Column('contract_type', sa.String(length=50), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('employee_type', sa.String(length=50), nullable=True),
        sa.Column('work_type', sa.String(length=50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_employment_contracts_employee_id', 'employment_contracts', ['employee_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_employment_contracts_employee_id', table_name='employment_contracts')
    op.drop_table('employment_contracts')
