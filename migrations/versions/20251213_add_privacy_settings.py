"""Add privacy_settings column to users table

Revision ID: 20251213_add_privacy_settings
Revises: 20251212_add_marital_and_expiry
Create Date: 2025-12-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251213_add_privacy_settings'
down_revision = '20251212_marital_expiry'
branch_labels = None
depends_on = None


def upgrade():
    # Add privacy_settings JSON column to users table
    op.add_column('users', sa.Column('privacy_settings', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('users', 'privacy_settings')
