"""update_org_fields_for_new_requirements

조직 관리 요구사항 변경:
- organizations: leader_phone 삭제, department_email 추가
- organization_type_configs: type_label -> type_label_ko, type_label_en 추가, is_active 삭제

Revision ID: 9abc123def45
Revises: 8fce810b6a8f
Create Date: 2026-01-10 19:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9abc123def45'
down_revision: Union[str, None] = '8fce810b6a8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === organizations 테이블 변경 ===
    # leader_phone 삭제 (조직장 내선번호 -> 대표 내선번호로 department_phone 사용)
    op.drop_column('organizations', 'leader_phone')

    # department_email 추가 (조직 이메일)
    op.add_column('organizations', sa.Column('department_email', sa.String(length=100), nullable=True))

    # === organization_type_configs 테이블 변경 ===
    # type_label -> type_label_ko 컬럼명 변경
    op.alter_column('organization_type_configs', 'type_label',
                    new_column_name='type_label_ko',
                    existing_type=sa.String(length=50),
                    existing_nullable=False)

    # type_label_en 추가 (영문명)
    op.add_column('organization_type_configs',
                  sa.Column('type_label_en', sa.String(length=50), nullable=True))

    # is_active 삭제 (활성화는 의미 없으므로 삭제)
    op.drop_column('organization_type_configs', 'is_active')


def downgrade() -> None:
    # === organization_type_configs 테이블 복원 ===
    # is_active 복원
    op.add_column('organization_type_configs',
                  sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True))

    # type_label_en 삭제
    op.drop_column('organization_type_configs', 'type_label_en')

    # type_label_ko -> type_label 컬럼명 복원
    op.alter_column('organization_type_configs', 'type_label_ko',
                    new_column_name='type_label',
                    existing_type=sa.String(length=50),
                    existing_nullable=False)

    # === organizations 테이블 복원 ===
    # department_email 삭제
    op.drop_column('organizations', 'department_email')

    # leader_phone 복원
    op.add_column('organizations', sa.Column('leader_phone', sa.String(length=20), nullable=True))
