"""add_test_data_schema_changes

Revision ID: 198e98fb90e4
Revises: corporate_settings_stage1
Create Date: 2025-12-20 12:30:51.613949+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '198e98fb90e4'
down_revision: Union[str, None] = 'corporate_settings_stage1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create personal_families table
    op.create_table('personal_families',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('relation', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('birth_date', sa.String(length=20), nullable=True),
        sa.Column('occupation', sa.String(length=100), nullable=True),
        sa.Column('education', sa.String(length=100), nullable=True),
        sa.Column('is_cohabitant', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_dependent', sa.Boolean(), nullable=True, default=False),
        sa.Column('contact', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['profile_id'], ['personal_profiles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personal_families_profile_id'), 'personal_families', ['profile_id'], unique=False)

    # 2. Add companies.logo column
    op.add_column('companies', sa.Column('logo', sa.String(length=255), nullable=True))

    # 3. Add personal_careers columns
    op.add_column('personal_careers', sa.Column('job_grade', sa.String(length=50), nullable=True))
    op.add_column('personal_careers', sa.Column('job_role', sa.String(length=100), nullable=True))
    op.add_column('personal_careers', sa.Column('salary', sa.Integer(), nullable=True))

    # 4. Add organizations.company_id column
    op.add_column('organizations', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_organizations_company', 'organizations', 'companies', ['company_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # 4. Drop organizations.company_id
    op.drop_constraint('fk_organizations_company', 'organizations', type_='foreignkey')
    op.drop_column('organizations', 'company_id')

    # 3. Drop personal_careers columns
    op.drop_column('personal_careers', 'salary')
    op.drop_column('personal_careers', 'job_role')
    op.drop_column('personal_careers', 'job_grade')

    # 2. Drop companies.logo
    op.drop_column('companies', 'logo')

    # 1. Drop personal_families table
    op.drop_index(op.f('ix_personal_families_profile_id'), table_name='personal_families')
    op.drop_table('personal_families')
