"""add_organization_type_config

Revision ID: 8fce810b6a8f
Revises: 4166adb6dad1
Create Date: 2026-01-10 16:55:26.115317+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fce810b6a8f'
down_revision: Union[str, None] = '4166adb6dad1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # organization_type_configs 테이블 생성
    op.create_table(
        'organization_type_configs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id'), nullable=False),
        sa.Column('type_code', sa.String(length=50), nullable=False),
        sa.Column('type_label', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('icon', sa.String(length=50), default='fa-folder'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # 인덱스 생성 (회사별 조회 최적화)
    op.create_index('ix_org_type_config_company', 'organization_type_configs', ['company_id'])
    op.create_index('ix_org_type_config_company_code', 'organization_type_configs', ['company_id', 'type_code'], unique=True)


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('ix_org_type_config_company_code', 'organization_type_configs')
    op.drop_index('ix_org_type_config_company', 'organization_type_configs')

    # 테이블 삭제
    op.drop_table('organization_type_configs')
