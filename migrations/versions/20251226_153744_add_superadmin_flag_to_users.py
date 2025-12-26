"""add_superadmin_flag_to_users

Revision ID: bf3c2419d5af
Revises: 545646fcc42c
Create Date: 2025-12-26 15:37:44.803814+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bf3c2419d5af'
down_revision: Union[str, None] = '545646fcc42c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_superadmin column to users table
    op.add_column('users', sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default='false'))
    op.create_index(op.f('ix_users_is_superadmin'), 'users', ['is_superadmin'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_is_superadmin'), table_name='users')
    op.drop_column('users', 'is_superadmin')
