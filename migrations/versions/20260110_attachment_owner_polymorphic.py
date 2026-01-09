"""attachment owner polymorphic

attachments 테이블에 owner_type + owner_id 범용 FK 구조 추가

Revision ID: 77ff8a1b2c3d
Revises: 32ffb06bafee
Create Date: 2026-01-10 12:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '77ff8a1b2c3d'
down_revision: Union[str, None] = '32ffb06bafee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 새 컬럼 추가 (nullable로 시작)
    op.add_column('attachments', sa.Column('owner_type', sa.String(50), nullable=True))
    op.add_column('attachments', sa.Column('owner_id', sa.Integer(), nullable=True))

    # 2. 기존 데이터 마이그레이션: employee_id -> owner_type='employee', owner_id=employee_id
    op.execute("UPDATE attachments SET owner_type = 'employee', owner_id = employee_id WHERE employee_id IS NOT NULL")

    # 3. NOT NULL 제약 추가 (기존 데이터 마이그레이션 후)
    op.alter_column('attachments', 'owner_type', nullable=False)
    op.alter_column('attachments', 'owner_id', nullable=False)

    # 4. employee_id를 nullable로 변경 (하위 호환성 유지)
    op.alter_column('attachments', 'employee_id', nullable=True)

    # 5. 새 인덱스 생성
    op.create_index('ix_attachments_owner', 'attachments', ['owner_type', 'owner_id'])
    op.create_index('ix_attachments_owner_category', 'attachments', ['owner_type', 'owner_id', 'category'])


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('ix_attachments_owner_category', table_name='attachments')
    op.drop_index('ix_attachments_owner', table_name='attachments')

    # employee_id를 NOT NULL로 복원
    op.alter_column('attachments', 'employee_id', nullable=False)

    # 새 컬럼 삭제
    op.drop_column('attachments', 'owner_id')
    op.drop_column('attachments', 'owner_type')
