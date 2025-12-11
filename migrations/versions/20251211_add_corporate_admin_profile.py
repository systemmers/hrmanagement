"""Add corporate_admin_profiles table

Revision ID: 7a1b2c3d4e5f
Revises: 8cc4c16df9d0
Create Date: 2025-12-11 10:30:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a1b2c3d4e5f'
down_revision: Union[str, None] = '8cc4c16df9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # corporate_admin_profiles 테이블 생성
    op.create_table('corporate_admin_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('english_name', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=50), nullable=True),
        sa.Column('mobile_phone', sa.String(length=20), nullable=True),
        sa.Column('office_phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=120), nullable=True),
        sa.Column('photo', sa.String(length=300), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_corporate_admin_profiles_user_id'), 'corporate_admin_profiles', ['user_id'], unique=True)
    op.create_index(op.f('ix_corporate_admin_profiles_company_id'), 'corporate_admin_profiles', ['company_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_corporate_admin_profiles_company_id'), table_name='corporate_admin_profiles')
    op.drop_index(op.f('ix_corporate_admin_profiles_user_id'), table_name='corporate_admin_profiles')
    op.drop_table('corporate_admin_profiles')
