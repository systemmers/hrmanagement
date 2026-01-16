"""
EmploymentContract Repository

근로계약 이력 데이터의 CRUD 기능을 제공합니다.
Phase 14: 인라인 편집 시스템 지원
"""
from typing import List
from app.domains.employee.models import EmploymentContract
from app.shared.repositories.base_repository import BaseRelationRepository


class EmploymentContractRepository(BaseRelationRepository[EmploymentContract]):
    """근로계약 이력 저장소"""

    def __init__(self):
        super().__init__(EmploymentContract)

    def find_by_contract_type(self, contract_type: str) -> List[EmploymentContract]:
        """특정 계약 유형의 모든 계약 조회"""
        return EmploymentContract.query.filter_by(contract_type=contract_type).all()
