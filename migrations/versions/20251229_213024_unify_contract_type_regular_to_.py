"""unify_contract_type_regular_to_employment

Revision ID: ea304f6be0d3
Revises: 2a3b4c5d6e7f
Create Date: 2025-12-29 21:30:24.153047+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea304f6be0d3'
down_revision: Union[str, None] = '2a3b4c5d6e7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    contract_type 값 통일: 'regular' -> 'employment'

    배경:
    - EMPLOYMENT_TYPE에서 'regular'='정규직' 사용
    - CONTRACT_TYPE에서 'employment'='정규직' 사용
    - DB에 두 값이 혼재하여 레이블 변환 및 필터 오류 발생

    영향:
    - 약 50건의 'regular' 값이 'employment'로 변경됨
    - 변경 후 모든 정규직 계약이 동일한 값 사용
    """
    op.execute("""
        UPDATE person_corporate_contracts
        SET contract_type = 'employment'
        WHERE contract_type = 'regular'
    """)


def downgrade() -> None:
    """
    원복 불가 - 데이터 정규화 작업으로 손실 없음

    참고: 원본 데이터가 'regular'였던 것과 원래 'employment'였던 것을
    구분할 수 없으므로 downgrade는 no-op으로 처리
    """
    pass
