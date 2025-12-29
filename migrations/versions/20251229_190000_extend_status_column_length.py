"""extend_status_column_length

status 컬럼 길이 확장 (VARCHAR(20) -> VARCHAR(30))
'termination_requested' 상태값 저장을 위해 필요 (21자)

Revision ID: 2a3b4c5d6e7f
Revises: 1caf06b1f9b3
Create Date: 2025-12-29 19:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, None] = '1caf06b1f9b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # status 컬럼 길이 확장: 20 -> 30
    op.alter_column('person_corporate_contracts', 'status',
                    existing_type=sa.String(20),
                    type_=sa.String(30),
                    existing_nullable=False)


def downgrade() -> None:
    # status 컬럼 길이 축소: 30 -> 20
    op.alter_column('person_corporate_contracts', 'status',
                    existing_type=sa.String(30),
                    type_=sa.String(20),
                    existing_nullable=False)
