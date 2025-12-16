"""Extend career fields for job hierarchy and salary system

Revision ID: 20251216_extend_career
Revises: 20251215_projects
Create Date: 2025-12-16

신규 필드:
- job_grade: 직급 (역량 레벨 - L3, 2호봉, Senior)
- job_title: 직책 (책임자 역할 - 팀장, 본부장, CFO)
- job_role: 직무 (수행 업무 - 인사기획, 회계관리)
- salary_type: 급여유형 (연봉제/월급제/시급제/호봉제)
- monthly_salary: 월급 (원)
- pay_step: 호봉 (급여 단계 1~50)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251216_extend_career'
down_revision = '20251215_projects'
branch_labels = None
depends_on = None


def upgrade():
    # 직급 체계 필드 추가
    op.add_column('careers', sa.Column('job_grade', sa.String(50), nullable=True))
    op.add_column('careers', sa.Column('job_title', sa.String(100), nullable=True))
    op.add_column('careers', sa.Column('job_role', sa.String(100), nullable=True))

    # 급여 체계 필드 추가
    op.add_column('careers', sa.Column('salary_type', sa.String(20), nullable=True))
    op.add_column('careers', sa.Column('monthly_salary', sa.Integer(), nullable=True))
    op.add_column('careers', sa.Column('pay_step', sa.Integer(), nullable=True))


def downgrade():
    # 급여 체계 필드 제거
    op.drop_column('careers', 'pay_step')
    op.drop_column('careers', 'monthly_salary')
    op.drop_column('careers', 'salary_type')

    # 직급 체계 필드 제거
    op.drop_column('careers', 'job_role')
    op.drop_column('careers', 'job_title')
    op.drop_column('careers', 'job_grade')
