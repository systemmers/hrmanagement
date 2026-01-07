"""
Contract Repositories Package (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.repositories import PersonContractRepository

Phase 2: 도메인 중심 마이그레이션 완료
"""
from app.domains.contract.repositories import PersonContractRepository

# Singleton instance
person_contract_repository = PersonContractRepository()

__all__ = ['PersonContractRepository', 'person_contract_repository']
