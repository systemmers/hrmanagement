"""
PersonCorporateContract Repository - 호환성 래퍼

[Compatibility Wrapper]
기존 import 경로 유지:
    from app.repositories.person_contract_repository import PersonContractRepository

Phase 2: 도메인 중심 마이그레이션 완료
새 코드는 아래 경로 사용 권장:
    from app.domains.contract.repositories import PersonContractRepository
"""
from app.domains.contract.repositories import PersonContractRepository

__all__ = ['PersonContractRepository']
