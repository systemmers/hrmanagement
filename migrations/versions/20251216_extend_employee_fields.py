"""Extend employee fields for job hierarchy consistency with Career model

Revision ID: 20251216_extend_employee
Revises: 20251216_extend_career
Create Date: 2025-12-16

Employee 소속정보에 직급 체계 필드 추가 (Career 모델과 일관성 유지)
- job_grade: 직급 (역량 레벨 - L3, 2호봉, Senior)
- job_role: 직무 (수행 업무 - 인사기획, 회계관리)

참고: position(직위), job_title(직책)은 이미 존재
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251216_extend_employee'
down_revision = '20251216_extend_career'
branch_labels = None
depends_on = None


def upgrade():
    # 직급 체계 필드 추가
    op.add_column('employees', sa.Column('job_grade', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('job_role', sa.String(100), nullable=True))


def downgrade():
    # 직급 체계 필드 제거
    op.drop_column('employees', 'job_role')
    op.drop_column('employees', 'job_grade')
