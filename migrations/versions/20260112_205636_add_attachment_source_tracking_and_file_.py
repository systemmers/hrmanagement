"""Add attachment source tracking and file sharing settings

Revision ID: fb5bc28b6c9c
Revises: 441c2451a638
Create Date: 2026-01-12 20:56:36.591131+09:00

Phase 33: 계약 기반 첨부파일 동기화/분리 지원
- Attachment 모델에 source 추적 필드 추가
- DataSharingSettings 모델에 파일 공유 설정 필드 추가
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'fb5bc28b6c9c'
down_revision: Union[str, None] = '441c2451a638'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Attachment 테이블: source 추적 필드 추가 ===

    # source_type: 출처 타입 (synced, corporate, personal)
    op.add_column('attachments', sa.Column(
        'source_type',
        sa.String(length=20),
        nullable=True,
        comment='출처 타입: synced(동기화), corporate(법인생성), personal(개인생성)'
    ))

    # source_contract_id: 동기화 출처 계약 ID (FK)
    op.add_column('attachments', sa.Column(
        'source_contract_id',
        sa.Integer(),
        nullable=True,
        comment='동기화 출처 계약 ID'
    ))

    # is_deletable_on_termination: 계약 해지 시 삭제 여부
    op.add_column('attachments', sa.Column(
        'is_deletable_on_termination',
        sa.Boolean(),
        nullable=False,
        server_default=sa.text('true'),
        comment='계약 해지 시 삭제 여부'
    ))

    # 인덱스 생성
    op.create_index(
        'ix_attachments_source_type',
        'attachments',
        ['source_type'],
        unique=False
    )
    op.create_index(
        'ix_attachments_source_contract_id',
        'attachments',
        ['source_contract_id'],
        unique=False
    )

    # FK 생성
    op.create_foreign_key(
        'fk_attachments_source_contract',
        'attachments',
        'person_corporate_contracts',
        ['source_contract_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # === DataSharingSettings 테이블: 파일 공유 설정 필드 추가 ===

    # share_profile_photo: 프로필 사진 공유 여부
    op.add_column('data_sharing_settings', sa.Column(
        'share_profile_photo',
        sa.Boolean(),
        nullable=False,
        server_default=sa.text('true'),
        comment='프로필 사진 공유 여부'
    ))

    # share_documents: 일반 첨부 문서 공유 여부
    op.add_column('data_sharing_settings', sa.Column(
        'share_documents',
        sa.Boolean(),
        nullable=False,
        server_default=sa.text('false'),
        comment='일반 첨부 문서 공유 여부'
    ))

    # share_certificate_files: 자격증 증빙 파일 공유 여부
    op.add_column('data_sharing_settings', sa.Column(
        'share_certificate_files',
        sa.Boolean(),
        nullable=False,
        server_default=sa.text('false'),
        comment='자격증 증빙 파일 공유 여부'
    ))


def downgrade() -> None:
    # === DataSharingSettings 테이블: 파일 공유 설정 필드 제거 ===
    op.drop_column('data_sharing_settings', 'share_certificate_files')
    op.drop_column('data_sharing_settings', 'share_documents')
    op.drop_column('data_sharing_settings', 'share_profile_photo')

    # === Attachment 테이블: source 추적 필드 제거 ===
    op.drop_constraint('fk_attachments_source_contract', 'attachments', type_='foreignkey')
    op.drop_index('ix_attachments_source_contract_id', table_name='attachments')
    op.drop_index('ix_attachments_source_type', table_name='attachments')
    op.drop_column('attachments', 'is_deletable_on_termination')
    op.drop_column('attachments', 'source_contract_id')
    op.drop_column('attachments', 'source_type')
