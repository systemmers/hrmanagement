"""add_termination_request_columns

양측 동의 계약 종료 기능을 위한 컬럼 추가 (Phase 5.3)

Revision ID: 1caf06b1f9b3
Revises: bf3c2419d5af
Create Date: 2025-12-29 18:39:38.387728+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1caf06b1f9b3'
down_revision: Union[str, None] = 'bf3c2419d5af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 양측 동의 계약 종료를 위한 컬럼 추가
    op.add_column('person_corporate_contracts',
        sa.Column('termination_requested_by', sa.Integer(), nullable=True))
    op.add_column('person_corporate_contracts',
        sa.Column('termination_requested_at', sa.DateTime(), nullable=True))
    op.add_column('person_corporate_contracts',
        sa.Column('termination_rejected_by', sa.Integer(), nullable=True))
    op.add_column('person_corporate_contracts',
        sa.Column('termination_rejected_at', sa.DateTime(), nullable=True))
    op.add_column('person_corporate_contracts',
        sa.Column('termination_rejection_reason', sa.Text(), nullable=True))

    # Foreign key 제약조건 추가
    op.create_foreign_key(
        'fk_pcc_termination_requested_by',
        'person_corporate_contracts', 'users',
        ['termination_requested_by'], ['id']
    )
    op.create_foreign_key(
        'fk_pcc_termination_rejected_by',
        'person_corporate_contracts', 'users',
        ['termination_rejected_by'], ['id']
    )


def downgrade() -> None:
    # Foreign key 제약조건 삭제
    op.drop_constraint('fk_pcc_termination_rejected_by', 'person_corporate_contracts', type_='foreignkey')
    op.drop_constraint('fk_pcc_termination_requested_by', 'person_corporate_contracts', type_='foreignkey')

    # 컬럼 삭제
    op.drop_column('person_corporate_contracts', 'termination_rejection_reason')
    op.drop_column('person_corporate_contracts', 'termination_rejected_at')
    op.drop_column('person_corporate_contracts', 'termination_rejected_by')
    op.drop_column('person_corporate_contracts', 'termination_requested_at')
    op.drop_column('person_corporate_contracts', 'termination_requested_by')
