"""Add actual_address, marital_status, emergency_contact fields and PersonalAward table

For profile unification:
- employees: marital_status, actual_address, emergency_contact
- personal_profiles: marital_status, actual_address, emergency_contact
- personal_awards: new table for personal award records

Revision ID: 20251213_add_profile_fields
Revises: 20251213_add_privacy_settings
Create Date: 2025-12-13
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251213_add_profile_fields'
down_revision = '20251213_add_privacy_settings'
branch_labels = None
depends_on = None


def upgrade():
    """Add new fields to employees and personal_profiles tables, create personal_awards table."""

    # Add fields to employees table
    op.add_column('employees', sa.Column('marital_status', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('actual_postal_code', sa.String(20), nullable=True))
    op.add_column('employees', sa.Column('actual_address', sa.String(500), nullable=True))
    op.add_column('employees', sa.Column('actual_detailed_address', sa.String(500), nullable=True))
    op.add_column('employees', sa.Column('emergency_contact', sa.String(50), nullable=True))
    op.add_column('employees', sa.Column('emergency_relation', sa.String(50), nullable=True))

    # Add fields to personal_profiles table
    op.add_column('personal_profiles', sa.Column('marital_status', sa.String(20), nullable=True))
    op.add_column('personal_profiles', sa.Column('actual_postal_code', sa.String(20), nullable=True))
    op.add_column('personal_profiles', sa.Column('actual_address', sa.String(500), nullable=True))
    op.add_column('personal_profiles', sa.Column('actual_detailed_address', sa.String(500), nullable=True))
    op.add_column('personal_profiles', sa.Column('emergency_contact', sa.String(50), nullable=True))
    op.add_column('personal_profiles', sa.Column('emergency_relation', sa.String(50), nullable=True))

    # Create personal_awards table
    op.create_table(
        'personal_awards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('award_name', sa.String(200), nullable=False),
        sa.Column('award_date', sa.String(20), nullable=True),
        sa.Column('institution', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['profile_id'], ['personal_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    """Remove added fields and table."""

    # Drop personal_awards table
    op.drop_table('personal_awards')

    # Remove fields from personal_profiles
    op.drop_column('personal_profiles', 'emergency_relation')
    op.drop_column('personal_profiles', 'emergency_contact')
    op.drop_column('personal_profiles', 'actual_detailed_address')
    op.drop_column('personal_profiles', 'actual_address')
    op.drop_column('personal_profiles', 'actual_postal_code')
    op.drop_column('personal_profiles', 'marital_status')

    # Remove fields from employees
    op.drop_column('employees', 'emergency_relation')
    op.drop_column('employees', 'emergency_contact')
    op.drop_column('employees', 'actual_detailed_address')
    op.drop_column('employees', 'actual_address')
    op.drop_column('employees', 'actual_postal_code')
    op.drop_column('employees', 'marital_status')
