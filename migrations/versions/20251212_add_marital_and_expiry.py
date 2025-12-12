"""Add marital_status and expiry_date fields

Revision ID: 20251212_marital_expiry
Revises: 20251212_add_fields
Create Date: 2025-12-12
"""
from alembic import op
import sqlalchemy as sa


revision = '20251212_marital_expiry'
down_revision = '20251212_add_fields'
branch_labels = None
depends_on = None


def upgrade():
    # employees.marital_status (single, married)
    op.add_column('employees', sa.Column('marital_status', sa.String(20), nullable=True))

    # personal_languages.expiry_date (어학 만료일)
    op.add_column('personal_languages', sa.Column('expiry_date', sa.String(20), nullable=True))


def downgrade():
    op.drop_column('personal_languages', 'expiry_date')
    op.drop_column('employees', 'marital_status')
