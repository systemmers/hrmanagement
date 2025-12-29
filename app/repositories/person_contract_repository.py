"""
PersonCorporateContract Repository - 호환성 래퍼

[Compatibility Wrapper]
기존 import 경로 유지:
    from app.repositories.person_contract_repository import PersonContractRepository

Phase 3 구조화: 실제 구현은 contract/ 폴더로 이동
새 코드는 아래 경로 사용 권장:
    from app.repositories.contract import PersonContractRepository
"""
from app.repositories.contract.person_contract_repository import PersonContractRepository

__all__ = ['PersonContractRepository']
