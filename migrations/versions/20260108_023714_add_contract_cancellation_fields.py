"""add contract cancellation fields

Revision ID: 32ffb06bafee
Revises: f1a2b3c4d5e6
Create Date: 2026-01-08 02:37:14.730053+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '32ffb06bafee'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 계약 요청 취소 기능을 위한 필드 추가
    op.add_column('person_corporate_contracts', sa.Column('cancellation_reason', sa.Text(), nullable=True))
    op.add_column('person_corporate_contracts', sa.Column('cancelled_at', sa.DateTime(), nullable=True))
    op.add_column('person_corporate_contracts', sa.Column('cancelled_by', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_person_corporate_contracts_cancelled_by',
        'person_corporate_contracts',
        'users',
        ['cancelled_by'],
        ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_person_corporate_contracts_cancelled_by', 'person_corporate_contracts', type_='foreignkey')
    op.drop_column('person_corporate_contracts', 'cancelled_by')
    op.drop_column('person_corporate_contracts', 'cancelled_at')
    op.drop_column('person_corporate_contracts', 'cancellation_reason')
