"""normalize_employee_status_values

Revision ID: 545646fcc42c
Revises: 10fe4aba3d57
Create Date: 2025-12-25 18:19:06.377663+09:00

Employee.status 값 정규화:
- '재직' -> 'active' (영문 코드로 통일)
- '퇴사' -> 'resigned' (영문 코드로 통일)

SSOT 원칙: FieldOptions.EMPLOYEE_STATUS의 영문 코드 사용
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '545646fcc42c'
down_revision: Union[str, None] = '10fe4aba3d57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """한글 상태값을 영문 코드로 정규화"""
    # '재직' -> 'active'
    op.execute("UPDATE employees SET status = 'active' WHERE status = '재직'")

    # '퇴사' -> 'resigned'
    op.execute("UPDATE employees SET status = 'resigned' WHERE status = '퇴사'")


def downgrade() -> None:
    """영문 코드를 한글 상태값으로 복원 (호환성)"""
    # 'active' -> '재직' (원래 '재직'이었던 것만 복원하기 어려우므로 전체 변환)
    # 주의: 원래 'active'였던 값도 '재직'으로 변환됨
    op.execute("UPDATE employees SET status = '재직' WHERE status = 'active'")

    # 'resigned' -> '퇴사'
    op.execute("UPDATE employees SET status = '퇴사' WHERE status = 'resigned'")
