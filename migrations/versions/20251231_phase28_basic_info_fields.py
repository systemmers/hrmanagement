"""phase28_basic_info_fields

Phase 28: 기본 정보 섹션 필드 개선

변경 내용:
1. 신규 컬럼 추가:
   - foreign_name: 외국어 이름 (영문 외)
   - age: 나이 (만 나이, 자동 계산)
   - bank_name: 은행명 (급여정보에서 이동)
   - account_number: 계좌번호 (급여정보에서 이동)
   - account_holder: 예금주 (급여정보에서 이동)

2. 삭제 컬럼:
   - blood_type: 혈액형 (요구사항에 따른 삭제)
   - religion: 종교 (요구사항에 따른 삭제)

대상 테이블: profiles, personal_profiles, employees

Revision ID: f1a2b3c4d5e6
Revises: ea304f6be0d3
Create Date: 2025-12-31 00:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'ea304f6be0d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Phase 28: 기본 정보 필드 개선

    1. 신규 컬럼 추가 (profiles, personal_profiles, employees)
    2. 삭제 컬럼 제거 (blood_type, religion)
    """

    # ==========================================================
    # 0. profiles 테이블 수정 (User 모델 관계용)
    # ==========================================================

    # 신규 컬럼 추가
    op.add_column('profiles',
        sa.Column('foreign_name', sa.String(100), nullable=True,
                  comment='외국어 이름 (영문 외 추가 외국어명)'))

    op.add_column('profiles',
        sa.Column('age', sa.Integer(), nullable=True,
                  comment='나이 (만 나이, 주민번호 기반 자동 계산)'))

    op.add_column('profiles',
        sa.Column('bank_name', sa.String(50), nullable=True,
                  comment='은행명'))

    op.add_column('profiles',
        sa.Column('account_number', sa.String(50), nullable=True,
                  comment='계좌번호'))

    op.add_column('profiles',
        sa.Column('account_holder', sa.String(50), nullable=True,
                  comment='예금주'))

    # 삭제 컬럼 제거 (데이터 손실 경고: blood_type, religion 데이터 삭제됨)
    op.drop_column('profiles', 'blood_type')
    op.drop_column('profiles', 'religion')

    # ==========================================================
    # 1. personal_profiles 테이블 수정
    # ==========================================================

    # 신규 컬럼 추가
    op.add_column('personal_profiles',
        sa.Column('foreign_name', sa.String(100), nullable=True,
                  comment='외국어 이름 (영문 외 추가 외국어명)'))

    op.add_column('personal_profiles',
        sa.Column('age', sa.Integer(), nullable=True,
                  comment='나이 (만 나이, 주민번호 기반 자동 계산)'))

    op.add_column('personal_profiles',
        sa.Column('bank_name', sa.String(50), nullable=True,
                  comment='은행명'))

    op.add_column('personal_profiles',
        sa.Column('account_number', sa.String(50), nullable=True,
                  comment='계좌번호'))

    op.add_column('personal_profiles',
        sa.Column('account_holder', sa.String(50), nullable=True,
                  comment='예금주'))

    # 삭제 컬럼 제거 (데이터 손실 경고: blood_type, religion 데이터 삭제됨)
    op.drop_column('personal_profiles', 'blood_type')
    op.drop_column('personal_profiles', 'religion')

    # ==========================================================
    # 2. employees 테이블 수정
    # ==========================================================

    # 신규 컬럼 추가
    op.add_column('employees',
        sa.Column('foreign_name', sa.String(100), nullable=True,
                  comment='외국어 이름 (영문 외 추가 외국어명)'))

    op.add_column('employees',
        sa.Column('age', sa.Integer(), nullable=True,
                  comment='나이 (만 나이, 주민번호 기반 자동 계산)'))

    op.add_column('employees',
        sa.Column('bank_name', sa.String(50), nullable=True,
                  comment='은행명'))

    op.add_column('employees',
        sa.Column('account_number', sa.String(50), nullable=True,
                  comment='계좌번호'))

    op.add_column('employees',
        sa.Column('account_holder', sa.String(50), nullable=True,
                  comment='예금주'))

    # 삭제 컬럼 제거 (데이터 손실 경고: blood_type, religion 데이터 삭제됨)
    op.drop_column('employees', 'blood_type')
    op.drop_column('employees', 'religion')

    print("Phase 28 마이그레이션 완료:")
    print("  - 대상 테이블: profiles, personal_profiles, employees")
    print("  - 신규 컬럼 5개 추가 (foreign_name, age, bank_name, account_number, account_holder)")
    print("  - 삭제 컬럼 2개 제거 (blood_type, religion)")


def downgrade() -> None:
    """
    Phase 28 롤백

    주의: blood_type, religion 데이터는 복구되지 않습니다.
    """

    # ==========================================================
    # 0. profiles 테이블 롤백
    # ==========================================================

    # 삭제된 컬럼 복원 (데이터 없음)
    op.add_column('profiles',
        sa.Column('blood_type', sa.String(10), nullable=True))

    op.add_column('profiles',
        sa.Column('religion', sa.String(50), nullable=True))

    # 신규 컬럼 제거
    op.drop_column('profiles', 'account_holder')
    op.drop_column('profiles', 'account_number')
    op.drop_column('profiles', 'bank_name')
    op.drop_column('profiles', 'age')
    op.drop_column('profiles', 'foreign_name')

    # ==========================================================
    # 1. employees 테이블 롤백
    # ==========================================================

    # 삭제된 컬럼 복원 (데이터 없음)
    op.add_column('employees',
        sa.Column('blood_type', sa.String(10), nullable=True))

    op.add_column('employees',
        sa.Column('religion', sa.String(50), nullable=True))

    # 신규 컬럼 제거
    op.drop_column('employees', 'account_holder')
    op.drop_column('employees', 'account_number')
    op.drop_column('employees', 'bank_name')
    op.drop_column('employees', 'age')
    op.drop_column('employees', 'foreign_name')

    # ==========================================================
    # 2. personal_profiles 테이블 롤백
    # ==========================================================

    # 삭제된 컬럼 복원 (데이터 없음)
    op.add_column('personal_profiles',
        sa.Column('blood_type', sa.String(10), nullable=True))

    op.add_column('personal_profiles',
        sa.Column('religion', sa.String(50), nullable=True))

    # 신규 컬럼 제거
    op.drop_column('personal_profiles', 'account_holder')
    op.drop_column('personal_profiles', 'account_number')
    op.drop_column('personal_profiles', 'bank_name')
    op.drop_column('personal_profiles', 'age')
    op.drop_column('personal_profiles', 'foreign_name')

    print("Phase 28 롤백 완료")
    print("  주의: blood_type, religion 데이터는 복구되지 않았습니다.")
