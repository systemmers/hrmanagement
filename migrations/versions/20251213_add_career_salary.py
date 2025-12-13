"""Add salary field to careers table

For form-detail field consistency:
- careers: salary column for previous job salary records

Revision ID: 20251213_add_career_salary
Revises: 20251213_add_profile_fields
Create Date: 2025-12-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251213_add_career_salary'
down_revision = '20251213_add_profile_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add salary field to careers table."""
    op.add_column('careers', sa.Column('salary', sa.Integer(), nullable=True))


def downgrade():
    """Remove salary field from careers table."""
    op.drop_column('careers', 'salary')
