"""add_linked_entity_to_attachments

Revision ID: 5bf4a06d5f9c
Revises: 4ae3f95c4e8b
Create Date: 2026-01-12 22:00:00.000000+09:00

Phase 4.2: 항목별 증빙 서류 연동 필드 추가
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bf4a06d5f9c'
down_revision: Union[str, None] = '4ae3f95c4e8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # linked_entity_type 컬럼 추가
    op.add_column('attachments', sa.Column(
        'linked_entity_type',
        sa.String(length=50),
        nullable=True,
        comment='연결된 엔티티 타입: education, career, certificate 등'
    ))

    # linked_entity_id 컬럼 추가
    op.add_column('attachments', sa.Column(
        'linked_entity_id',
        sa.Integer(),
        nullable=True,
        comment='연결된 엔티티 ID'
    ))

    # 인덱스 생성
    op.create_index(
        'ix_attachments_linked_entity_type',
        'attachments',
        ['linked_entity_type'],
        unique=False
    )
    op.create_index(
        'ix_attachments_linked_entity_id',
        'attachments',
        ['linked_entity_id'],
        unique=False
    )
    # 복합 인덱스 (자주 사용되는 조회 패턴용)
    op.create_index(
        'ix_attachments_linked_entity',
        'attachments',
        ['linked_entity_type', 'linked_entity_id'],
        unique=False
    )


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('ix_attachments_linked_entity', table_name='attachments')
    op.drop_index('ix_attachments_linked_entity_id', table_name='attachments')
    op.drop_index('ix_attachments_linked_entity_type', table_name='attachments')

    # 컬럼 삭제
    op.drop_column('attachments', 'linked_entity_id')
    op.drop_column('attachments', 'linked_entity_type')
