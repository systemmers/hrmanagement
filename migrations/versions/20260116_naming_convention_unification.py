"""Phase 0.7: naming convention unification

Boolean fields: is_ prefix (state), has_ prefix (possession)
Date fields: _date suffix for dates, _at suffix for timestamps

Changes:
- employees.lunar_birth -> is_lunar_birth
- employees.probation_end -> probation_end_date
- personal_profiles.lunar_birth -> is_lunar_birth
- profiles.lunar_birth -> is_lunar_birth
- insurances.national_pension -> has_national_pension
- insurances.health_insurance -> has_health_insurance
- insurances.employment_insurance -> has_employment_insurance
- insurances.industrial_accident -> has_industrial_accident
- users.last_login -> last_login_at

Revision ID: 7f8a9b0c1d2e
Revises: 42bb3326914c
Create Date: 2026-01-16 12:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f8a9b0c1d2e'
down_revision: Union[str, None] = '42bb3326914c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Phase 0.5: phone -> mobile_phone 데이터 동기화
    # mobile_phone이 NULL인 경우 phone 값을 복사
    op.execute("""
        UPDATE employees
        SET mobile_phone = phone
        WHERE mobile_phone IS NULL AND phone IS NOT NULL
    """)

    # Phase 3.1: Boolean field prefix unification

    # employees.lunar_birth -> is_lunar_birth
    op.alter_column('employees', 'lunar_birth',
                    new_column_name='is_lunar_birth',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # employees.probation_end -> probation_end_date
    op.alter_column('employees', 'probation_end',
                    new_column_name='probation_end_date',
                    existing_type=sa.Date(),
                    existing_nullable=True)

    # personal_profiles.lunar_birth -> is_lunar_birth
    op.alter_column('personal_profiles', 'lunar_birth',
                    new_column_name='is_lunar_birth',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # profiles.lunar_birth -> is_lunar_birth (통합 프로필 테이블)
    op.alter_column('profiles', 'lunar_birth',
                    new_column_name='is_lunar_birth',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # insurances boolean fields -> has_ prefix
    op.alter_column('insurances', 'national_pension',
                    new_column_name='has_national_pension',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    op.alter_column('insurances', 'health_insurance',
                    new_column_name='has_health_insurance',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    op.alter_column('insurances', 'employment_insurance',
                    new_column_name='has_employment_insurance',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    op.alter_column('insurances', 'industrial_accident',
                    new_column_name='has_industrial_accident',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # Phase 3.2: Date suffix unification
    # users.last_login -> last_login_at
    op.alter_column('users', 'last_login',
                    new_column_name='last_login_at',
                    existing_type=sa.DateTime(),
                    existing_nullable=True)


def downgrade() -> None:
    # Reverse all column renames

    # users.last_login_at -> last_login
    op.alter_column('users', 'last_login_at',
                    new_column_name='last_login',
                    existing_type=sa.DateTime(),
                    existing_nullable=True)

    # insurances has_ prefix -> original names
    op.alter_column('insurances', 'has_industrial_accident',
                    new_column_name='industrial_accident',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    op.alter_column('insurances', 'has_employment_insurance',
                    new_column_name='employment_insurance',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    op.alter_column('insurances', 'has_health_insurance',
                    new_column_name='health_insurance',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    op.alter_column('insurances', 'has_national_pension',
                    new_column_name='national_pension',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # profiles.is_lunar_birth -> lunar_birth (통합 프로필 테이블)
    op.alter_column('profiles', 'is_lunar_birth',
                    new_column_name='lunar_birth',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # personal_profiles.is_lunar_birth -> lunar_birth
    op.alter_column('personal_profiles', 'is_lunar_birth',
                    new_column_name='lunar_birth',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)

    # employees.probation_end_date -> probation_end
    op.alter_column('employees', 'probation_end_date',
                    new_column_name='probation_end',
                    existing_type=sa.Date(),
                    existing_nullable=True)

    # employees.is_lunar_birth -> lunar_birth
    op.alter_column('employees', 'is_lunar_birth',
                    new_column_name='lunar_birth',
                    existing_type=sa.Boolean(),
                    existing_nullable=True)
