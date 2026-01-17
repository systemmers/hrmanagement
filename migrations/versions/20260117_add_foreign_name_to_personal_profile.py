"""Add foreign_name to personal_profiles

Phase 0.8: FieldRegistry 일관성 - personal_profiles 테이블에 foreign_name 컬럼 추가

Revision ID: 0k1l2m3n4o5p
Revises: 9h0c1d2e3f4g
Create Date: 2026-01-17
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0k1l2m3n4o5p'
down_revision = '9h0c1d2e3f4g'
branch_labels = None
depends_on = None


def upgrade():
    """Add foreign_name column to personal_profiles table"""
    # personal_profiles 테이블에 foreign_name 컬럼 추가
    # 컬럼이 이미 존재하는 경우 무시 (idempotent)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('personal_profiles')]

    if 'foreign_name' not in columns:
        op.add_column(
            'personal_profiles',
            sa.Column('foreign_name', sa.String(100), nullable=True)
        )


def downgrade():
    """Remove foreign_name column from personal_profiles table"""
    op.drop_column('personal_profiles', 'foreign_name')
