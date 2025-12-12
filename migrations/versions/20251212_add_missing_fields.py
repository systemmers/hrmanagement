"""Add missing fields for field consistency

- educations.gpa
- military_services.specialty
- personal_military_services.military_status
- personal_military_services.exemption_reason

Revision ID: 20251212_add_fields
Revises: 20251211_add_contract_snapshots
Create Date: 2025-12-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251212_add_fields'
down_revision = '8b2c3d4e5f6a'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing fields to education, military_service, personal_military_service tables."""
    # Add gpa to educations table
    op.add_column('educations', sa.Column('gpa', sa.String(20), nullable=True))

    # Add specialty to military_services table
    op.add_column('military_services', sa.Column('specialty', sa.String(200), nullable=True))

    # Add military_status and exemption_reason to personal_military_services table
    op.add_column('personal_military_services', sa.Column('military_status', sa.String(50), nullable=True))
    op.add_column('personal_military_services', sa.Column('exemption_reason', sa.String(500), nullable=True))


def downgrade():
    """Remove added fields."""
    # Remove from personal_military_services
    op.drop_column('personal_military_services', 'exemption_reason')
    op.drop_column('personal_military_services', 'military_status')

    # Remove from military_services
    op.drop_column('military_services', 'specialty')

    # Remove from educations
    op.drop_column('educations', 'gpa')
