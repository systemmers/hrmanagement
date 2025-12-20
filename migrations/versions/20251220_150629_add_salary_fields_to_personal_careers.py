"""add_salary_fields_to_personal_careers

Revision ID: 05723f2e7571
Revises: 198e98fb90e4
Create Date: 2025-12-20 15:06:29.637416+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05723f2e7571'
down_revision: Union[str, None] = '198e98fb90e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # personal_careers 테이블에 급여 관련 컬럼 추가
    op.add_column('personal_careers', sa.Column('salary_type', sa.String(length=50), nullable=True))
    op.add_column('personal_careers', sa.Column('monthly_salary', sa.Integer(), nullable=True))
    op.add_column('personal_careers', sa.Column('pay_step', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('personal_careers', 'pay_step')
    op.drop_column('personal_careers', 'monthly_salary')
    op.drop_column('personal_careers', 'salary_type')
