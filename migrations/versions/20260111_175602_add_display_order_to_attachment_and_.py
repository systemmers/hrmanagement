"""add display_order to attachment and relation models

Revision ID: 441c2451a638
Revises: 9abc123def45
Create Date: 2026-01-11 17:56:02.309112+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '441c2451a638'
down_revision: Union[str, None] = '9abc123def45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add display_order field to attachment and relation models."""
    # attachments 테이블에 display_order 추가
    op.add_column('attachments', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))

    # careers 테이블에 display_order 추가
    op.add_column('careers', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))

    # certificates 테이블에 display_order 추가
    op.add_column('certificates', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))

    # educations 테이블에 display_order 추가
    op.add_column('educations', sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Remove display_order field from attachment and relation models."""
    op.drop_column('educations', 'display_order')
    op.drop_column('certificates', 'display_order')
    op.drop_column('careers', 'display_order')
    op.drop_column('attachments', 'display_order')
