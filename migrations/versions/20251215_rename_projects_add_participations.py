"""Rename projects to hr_projects and add project_participations table

Revision ID: 20251215_projects
Revises: 20251213_add_career_salary
Create Date: 2025-12-15

- projects 테이블을 hr_projects로 이름 변경
- project_participations 테이블 신규 생성
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251215_projects'
down_revision = '20251213_add_career_salary'
branch_labels = None
depends_on = None


def upgrade():
    # 1. projects 테이블을 hr_projects로 이름 변경
    op.rename_table('projects', 'hr_projects')

    # 2. project_participations 테이블 생성
    op.create_table(
        'project_participations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(200), nullable=True),
        sa.Column('start_date', sa.String(20), nullable=True),
        sa.Column('end_date', sa.String(20), nullable=True),
        sa.Column('duration', sa.String(50), nullable=True),
        sa.Column('role', sa.String(100), nullable=True),
        sa.Column('duty', sa.String(200), nullable=True),
        sa.Column('client', sa.String(200), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # 인덱스 생성
    op.create_index(
        'ix_project_participations_employee_id',
        'project_participations',
        ['employee_id']
    )


def downgrade():
    # 1. project_participations 테이블 삭제
    op.drop_index('ix_project_participations_employee_id', table_name='project_participations')
    op.drop_table('project_participations')

    # 2. hr_projects 테이블을 projects로 이름 복원
    op.rename_table('hr_projects', 'projects')
