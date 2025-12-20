"""phase3_unified_profile_schema

Phase 3: 통합 프로필 스키마
- profiles 테이블 생성 (personal_profiles 구조 기반)
- employees 테이블에 profile_id, 스냅샷 컬럼 추가
- 외래키 및 인덱스 설정

Revision ID: a1b2c3d4e5f6
Revises: 05723f2e7571
Create Date: 2025-12-20

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '05723f2e7571'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================
    # Step 1: profiles 테이블 생성
    # ========================================
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),  # nullable for corp-created employees

        # 기본 개인정보
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('english_name', sa.String(length=100), nullable=True),
        sa.Column('chinese_name', sa.String(length=100), nullable=True),
        sa.Column('photo', sa.String(length=500), nullable=True),

        # 생년월일 정보
        sa.Column('birth_date', sa.String(length=20), nullable=True),
        sa.Column('lunar_birth', sa.Boolean(), default=False),
        sa.Column('gender', sa.String(length=10), nullable=True),

        # 연락처 정보
        sa.Column('mobile_phone', sa.String(length=50), nullable=True),
        sa.Column('home_phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),

        # 주소 정보
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('detailed_address', sa.String(length=500), nullable=True),

        # 신분 정보
        sa.Column('resident_number', sa.String(length=20), nullable=True),
        sa.Column('nationality', sa.String(length=50), nullable=True),

        # 기타 개인정보
        sa.Column('blood_type', sa.String(length=10), nullable=True),
        sa.Column('religion', sa.String(length=50), nullable=True),
        sa.Column('hobby', sa.String(length=200), nullable=True),
        sa.Column('specialty', sa.String(length=200), nullable=True),
        sa.Column('disability_info', sa.Text(), nullable=True),
        sa.Column('marital_status', sa.String(length=20), nullable=True),

        # 실제 거주 주소
        sa.Column('actual_postal_code', sa.String(length=20), nullable=True),
        sa.Column('actual_address', sa.String(length=500), nullable=True),
        sa.Column('actual_detailed_address', sa.String(length=500), nullable=True),

        # 비상연락처
        sa.Column('emergency_contact', sa.String(length=50), nullable=True),
        sa.Column('emergency_relation', sa.String(length=50), nullable=True),

        # 메타 정보
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_profiles_user_id'),
    )

    # profiles 인덱스
    op.create_index('ix_profiles_user_id', 'profiles', ['user_id'], unique=False)
    op.create_index('ix_profiles_name', 'profiles', ['name'], unique=False)
    op.create_index('ix_profiles_email', 'profiles', ['email'], unique=False)

    # ========================================
    # Step 2: employees 테이블에 컬럼 추가
    # ========================================

    # profile_id 컬럼 추가 (통합 프로필 연결)
    op.add_column('employees', sa.Column('profile_id', sa.Integer(), nullable=True))

    # 스냅샷 관련 컬럼 추가 (퇴사자 데이터 보관용)
    op.add_column('employees', sa.Column('profile_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('employees', sa.Column('snapshot_at', sa.DateTime(), nullable=True))
    op.add_column('employees', sa.Column('resignation_date', sa.Date(), nullable=True))
    op.add_column('employees', sa.Column('data_retention_until', sa.Date(), nullable=True))

    # 외래키 추가
    op.create_foreign_key(
        'fk_employees_profile_id',
        'employees', 'profiles',
        ['profile_id'], ['id'],
        ondelete='SET NULL'
    )

    # 인덱스 추가
    op.create_index('ix_employees_profile_id', 'employees', ['profile_id'], unique=False)
    op.create_index('ix_employees_resignation_date', 'employees', ['resignation_date'], unique=False)
    op.create_index('ix_employees_data_retention', 'employees', ['data_retention_until'], unique=False)


def downgrade() -> None:
    # employees 컬럼 제거
    op.drop_index('ix_employees_data_retention', table_name='employees')
    op.drop_index('ix_employees_resignation_date', table_name='employees')
    op.drop_index('ix_employees_profile_id', table_name='employees')
    op.drop_constraint('fk_employees_profile_id', 'employees', type_='foreignkey')

    op.drop_column('employees', 'data_retention_until')
    op.drop_column('employees', 'resignation_date')
    op.drop_column('employees', 'snapshot_at')
    op.drop_column('employees', 'profile_snapshot')
    op.drop_column('employees', 'profile_id')

    # profiles 테이블 제거
    op.drop_index('ix_profiles_email', table_name='profiles')
    op.drop_index('ix_profiles_name', table_name='profiles')
    op.drop_index('ix_profiles_user_id', table_name='profiles')
    op.drop_table('profiles')
