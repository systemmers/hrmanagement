"""add_org_phone_fields

Revision ID: 4166adb6dad1
Revises: 77ff8a1b2c3d
Create Date: 2026-01-10 16:29:52.226296+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4166adb6dad1'
down_revision: Union[str, None] = '77ff8a1b2c3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # organizations 테이블에 내선번호 필드 추가
    op.add_column('organizations', sa.Column('leader_phone', sa.String(length=20), nullable=True))
    op.add_column('organizations', sa.Column('department_phone', sa.String(length=20), nullable=True))


def downgrade() -> None:
    # 내선번호 필드 제거
    op.drop_column('organizations', 'department_phone')
    op.drop_column('organizations', 'leader_phone')
