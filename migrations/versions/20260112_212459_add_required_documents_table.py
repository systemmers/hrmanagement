"""add_required_documents_table

Revision ID: 4ae3f95c4e8b
Revises: fb5bc28b6c9c
Create Date: 2026-01-12 21:24:59.045073+09:00

Phase 4.1: 필수 서류 설정 테이블 추가
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ae3f95c4e8b'
down_revision: Union[str, None] = 'fb5bc28b6c9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # required_documents 테이블 생성
    op.create_table(
        'required_documents',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='서류명'),
        sa.Column('category', sa.String(length=50), nullable=True, comment='서류 분류'),
        sa.Column('description', sa.Text(), nullable=True, comment='설명'),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='필수 여부'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='표시 순서'),
        sa.Column('linked_entity_type', sa.String(length=50), nullable=True, comment='연결 엔티티 타입'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='활성화 여부'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], name='fk_required_documents_company'),
        sa.PrimaryKeyConstraint('id')
    )

    # 인덱스 생성
    op.create_index('ix_required_documents_company_id', 'required_documents', ['company_id'], unique=False)
    op.create_index('ix_required_documents_category', 'required_documents', ['category'], unique=False)
    op.create_index('ix_required_documents_linked_entity_type', 'required_documents', ['linked_entity_type'], unique=False)


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('ix_required_documents_linked_entity_type', table_name='required_documents')
    op.drop_index('ix_required_documents_category', table_name='required_documents')
    op.drop_index('ix_required_documents_company_id', table_name='required_documents')

    # 테이블 삭제
    op.drop_table('required_documents')
