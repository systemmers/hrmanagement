"""
법인 세팅 기능 Stage 1: DB 스키마 확장

1.1 classification_options 테이블 확장
1.2 company_settings 테이블 생성
1.3 number_categories 테이블 생성
1.4 number_registry 테이블 생성
1.5 ip_ranges 테이블 생성
1.6 ip_assignments 테이블 생성
1.7 company_documents 테이블 생성
1.8 company_visibility_settings 테이블 생성

Revision ID: corporate_settings_stage1
Revises: 20251216_extend_employee_fields
Create Date: 2025-12-16
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers
revision = 'corporate_settings_stage1'
down_revision = '20251216_extend_employee'
branch_labels = None
depends_on = None


def upgrade():
    # ============================================================
    # 1.1 classification_options 테이블 확장
    # ============================================================

    # company_id 컬럼 추가 (nullable - 기존 데이터는 NULL로 유지)
    op.add_column('classification_options',
        sa.Column('company_id', sa.Integer(), nullable=True)
    )

    # is_active 컬럼 추가
    op.add_column('classification_options',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1')
    )

    # is_system 컬럼 추가 (시스템 기본 제공 옵션 여부)
    op.add_column('classification_options',
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='0')
    )

    # created_at 컬럼 추가
    op.add_column('classification_options',
        sa.Column('created_at', sa.DateTime(), nullable=True)
    )

    # 외래키 추가
    op.create_foreign_key(
        'fk_classification_options_company',
        'classification_options', 'companies',
        ['company_id'], ['id'],
        ondelete='CASCADE'
    )

    # 인덱스 추가 (company_id, category)
    op.create_index(
        'idx_classification_company_category',
        'classification_options',
        ['company_id', 'category']
    )

    # 기존 데이터를 시스템 옵션으로 표시
    op.execute("""
        UPDATE classification_options
        SET is_system = true, created_at = CURRENT_TIMESTAMP
        WHERE company_id IS NULL
    """)

    # ============================================================
    # 1.2 company_settings 테이블 생성
    # ============================================================
    op.create_table('company_settings',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('value_type', sa.String(20), nullable=False, server_default='string'),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', 'key', name='uq_company_settings_key')
    )
    op.create_index('idx_company_settings_category', 'company_settings', ['company_id', 'category'])

    # ============================================================
    # 1.3 number_categories 테이블 생성 (분류코드 관리)
    # ============================================================
    op.create_table('number_categories',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),  # employee_number, asset_number
        sa.Column('code', sa.String(6), nullable=False),   # 분류코드 (NB, DT, DEPT 등)
        sa.Column('name', sa.String(100), nullable=False), # 분류명
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('current_sequence', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', 'type', 'code', name='uq_number_category')
    )
    op.create_index('idx_number_categories_type', 'number_categories', ['company_id', 'type'])

    # ============================================================
    # 1.4 number_registry 테이블 생성 (번호 레지스트리)
    # ============================================================
    op.create_table('number_registry',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('full_number', sa.String(50), nullable=False),  # 전체 번호 (ABC-NB-000001)
        sa.Column('sequence', sa.Integer(), nullable=False),       # 순번
        sa.Column('status', sa.String(20), nullable=False, server_default='available'),  # available, in_use, retired
        sa.Column('assigned_to_type', sa.String(20), nullable=True),  # employee, asset
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('retired_at', sa.DateTime(), nullable=True),
        sa.Column('retired_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['number_categories.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', 'category_id', 'sequence', name='uq_number_registry_seq')
    )
    op.create_index('idx_number_registry_status', 'number_registry', ['company_id', 'category_id', 'status'])
    op.create_index('idx_number_registry_full', 'number_registry', ['company_id', 'full_number'])

    # ============================================================
    # 1.5 ip_ranges 테이블 생성 (IP 범위 관리)
    # ============================================================
    op.create_table('ip_ranges',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('range_start', sa.String(15), nullable=False),  # 192.168.1.1
        sa.Column('range_end', sa.String(15), nullable=False),    # 192.168.1.100
        sa.Column('subnet', sa.String(15), nullable=True),        # 255.255.255.0
        sa.Column('gateway', sa.String(15), nullable=True),       # 192.168.1.1
        sa.Column('label', sa.String(100), nullable=True),        # 부서 라벨
        sa.Column('ip_count', sa.Integer(), nullable=True),       # 자동 계산된 IP 개수
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE')
    )
    op.create_index('idx_ip_ranges_company', 'ip_ranges', ['company_id'])

    # ============================================================
    # 1.6 ip_assignments 테이블 생성 (IP 할당 관리)
    # ============================================================
    op.create_table('ip_assignments',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('range_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(15), nullable=False),  # 할당된 IP
        sa.Column('status', sa.String(20), nullable=False, server_default='available'),  # available, in_use, retired
        sa.Column('assigned_to_type', sa.String(20), nullable=True),  # employee, asset
        sa.Column('assigned_to_id', sa.Integer(), nullable=True),
        sa.Column('assigned_at', sa.DateTime(), nullable=True),
        sa.Column('retired_at', sa.DateTime(), nullable=True),
        sa.Column('retired_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['range_id'], ['ip_ranges.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', 'ip_address', name='uq_ip_assignments_address')
    )
    op.create_index('idx_ip_assignments_status', 'ip_assignments', ['company_id', 'range_id', 'status'])

    # ============================================================
    # 1.7 company_documents 테이블 생성 (법인 서류)
    # ============================================================
    op.create_table('company_documents',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),        # required, payroll, welfare, security, other
        sa.Column('document_type', sa.String(100), nullable=False),  # 서류 유형 코드
        sa.Column('title', sa.String(200), nullable=False),          # 서류 제목
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),       # 파일 경로
        sa.Column('file_name', sa.String(200), nullable=True),       # 원본 파일명
        sa.Column('file_size', sa.Integer(), nullable=True),         # 파일 크기
        sa.Column('file_type', sa.String(50), nullable=True),        # 파일 확장자
        sa.Column('version', sa.String(20), nullable=True),          # 버전
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='0'),  # 필수 서명 여부
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('visibility', sa.String(20), nullable=False, server_default='all'),  # all, admin, manager
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        # AI 자동 세팅 관련 필드
        sa.Column('is_electronic', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('ai_processed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('ai_detected_type', sa.String(100), nullable=True),
        sa.Column('ai_extracted_data', sa.JSON(), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('original_file_path', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL')
    )
    op.create_index('idx_company_documents', 'company_documents', ['company_id', 'category'])

    # ============================================================
    # 1.8 company_visibility_settings 테이블 생성 (노출 설정)
    # ============================================================
    op.create_table('company_visibility_settings',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('salary_visibility', sa.String(20), nullable=False, server_default='self_only'),
        sa.Column('evaluation_visibility', sa.String(20), nullable=False, server_default='self_only'),
        sa.Column('org_chart_visibility', sa.String(20), nullable=False, server_default='all'),
        sa.Column('contact_visibility', sa.String(20), nullable=False, server_default='team'),
        sa.Column('document_visibility', sa.String(20), nullable=False, server_default='all'),
        sa.Column('show_salary_to_managers', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('show_evaluation_to_managers', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('company_id', name='uq_company_visibility')
    )


def downgrade():
    # 역순으로 테이블 삭제
    op.drop_table('company_visibility_settings')
    op.drop_table('company_documents')
    op.drop_table('ip_assignments')
    op.drop_table('ip_ranges')
    op.drop_table('number_registry')
    op.drop_table('number_categories')
    op.drop_table('company_settings')

    # classification_options 컬럼 제거
    op.drop_index('idx_classification_company_category', 'classification_options')
    op.drop_constraint('fk_classification_options_company', 'classification_options', type_='foreignkey')
    op.drop_column('classification_options', 'created_at')
    op.drop_column('classification_options', 'is_system')
    op.drop_column('classification_options', 'is_active')
    op.drop_column('classification_options', 'company_id')
