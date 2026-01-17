"""Phase 0.7: Field cleanup and military integration

삭제할 필드 (4개):
- chinese_name, home_phone, postal_code, account_holder

추가할 필드 (2개, 3개 테이블):
- military_status: 병역여부 (군필/미필/면제/해당없음)
- note: 비고

삭제할 테이블:
- military_services (MilitaryService 모델 통합)

Revision ID: 9h0c1d2e3f4g
Revises: 8g9b0c1d2e3f
Create Date: 2026-01-16 18:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9h0c1d2e3f4g'
down_revision: Union[str, None] = '8g9b0c1d2e3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # 1. employees 테이블 변경
    # ========================================

    # 삭제할 컬럼
    op.drop_column('employees', 'chinese_name')
    op.drop_column('employees', 'home_phone')
    op.drop_column('employees', 'postal_code')
    op.drop_column('employees', 'account_holder')

    # 추가할 컬럼 (병역 및 비고)
    op.add_column('employees', sa.Column('military_status', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('note', sa.Text(), nullable=True))

    # ========================================
    # 2. profiles 테이블 변경
    # ========================================

    # 삭제할 컬럼
    op.drop_column('profiles', 'chinese_name')
    op.drop_column('profiles', 'home_phone')
    op.drop_column('profiles', 'postal_code')

    # 추가할 컬럼 (병역 및 비고)
    op.add_column('profiles', sa.Column('military_status', sa.String(50), nullable=True))
    op.add_column('profiles', sa.Column('note', sa.Text(), nullable=True))

    # ========================================
    # 3. personal_profiles 테이블 변경
    # ========================================

    # 삭제할 컬럼
    op.drop_column('personal_profiles', 'chinese_name')
    op.drop_column('personal_profiles', 'home_phone')
    op.drop_column('personal_profiles', 'postal_code')

    # 추가할 컬럼 (병역 및 비고)
    op.add_column('personal_profiles', sa.Column('military_status', sa.String(50), nullable=True))
    op.add_column('personal_profiles', sa.Column('note', sa.Text(), nullable=True))

    # ========================================
    # 4. military_services 테이블 삭제
    # ========================================
    # 먼저 기존 데이터를 employees.military_status로 마이그레이션
    op.execute("""
        UPDATE employees e
        SET military_status = (
            SELECT ms.military_status
            FROM military_services ms
            WHERE ms.employee_id = e.id
        )
        WHERE EXISTS (
            SELECT 1 FROM military_services ms WHERE ms.employee_id = e.id
        )
    """)

    # military_services 테이블 삭제
    op.drop_table('military_services')


def downgrade() -> None:
    # ========================================
    # 1. military_services 테이블 재생성
    # ========================================
    op.create_table('military_services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('military_status', sa.String(50), nullable=True),
        sa.Column('branch', sa.String(50), nullable=True),
        sa.Column('rank', sa.String(50), nullable=True),
        sa.Column('enlistment_date', sa.String(20), nullable=True),
        sa.Column('discharge_date', sa.String(20), nullable=True),
        sa.Column('service_type', sa.String(100), nullable=True),
        sa.Column('specialty', sa.String(100), nullable=True),
        sa.Column('exemption_reason', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], )
    )

    # ========================================
    # 2. personal_profiles 테이블 복원
    # ========================================
    op.drop_column('personal_profiles', 'note')
    op.drop_column('personal_profiles', 'military_status')

    op.add_column('personal_profiles', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('personal_profiles', sa.Column('home_phone', sa.String(50), nullable=True))
    op.add_column('personal_profiles', sa.Column('chinese_name', sa.String(100), nullable=True))

    # ========================================
    # 3. profiles 테이블 복원
    # ========================================
    op.drop_column('profiles', 'note')
    op.drop_column('profiles', 'military_status')

    op.add_column('profiles', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('profiles', sa.Column('home_phone', sa.String(50), nullable=True))
    op.add_column('profiles', sa.Column('chinese_name', sa.String(100), nullable=True))

    # ========================================
    # 4. employees 테이블 복원
    # ========================================
    op.drop_column('employees', 'note')
    op.drop_column('employees', 'military_status')

    op.add_column('employees', sa.Column('account_holder', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('postal_code', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('home_phone', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('chinese_name', sa.String(100), nullable=True))
