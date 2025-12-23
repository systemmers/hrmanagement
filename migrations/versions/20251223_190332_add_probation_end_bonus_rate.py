"""add_probation_end_bonus_rate

Revision ID: 9315d80ecc3e
Revises: e6f7dc2bfa1d
Create Date: 2025-12-23 19:03:32.471753+09:00

Employee에 probation_end(수습종료일), Salary에 bonus_rate(상여금률) 컬럼 추가
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9315d80ecc3e'
down_revision: Union[str, None] = 'e6f7dc2bfa1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Employee 모델에 probation_end 컬럼 추가
    op.add_column('employees', sa.Column('probation_end', sa.Date(), nullable=True))

    # Salary 모델에 bonus_rate 컬럼 추가
    op.add_column('salaries', sa.Column('bonus_rate', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('salaries', 'bonus_rate')
    op.drop_column('employees', 'probation_end')
