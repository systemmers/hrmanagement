"""Remove snapshot columns from employees table

Revision ID: remove_snapshot_cols
Revises: 9315d80ecc3e
Create Date: 2024-12-24

스냅샷 기능 제거에 따른 컬럼 삭제
- profile_snapshot (JSONB)
- snapshot_at (DateTime)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'remove_snapshot_cols'
down_revision = '9315d80ecc3e'
branch_labels = None
depends_on = None


def upgrade():
    """스냅샷 컬럼 제거"""
    op.drop_column('employees', 'snapshot_at')
    op.drop_column('employees', 'profile_snapshot')


def downgrade():
    """스냅샷 컬럼 복원"""
    op.add_column('employees', sa.Column('profile_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('employees', sa.Column('snapshot_at', sa.DateTime(), nullable=True))
