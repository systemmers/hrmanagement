"""
Contract Core Service (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.services import ContractCoreService
"""
from app.domains.contract.services.contract_core_service import ContractCoreService

contract_core_service = ContractCoreService()

__all__ = ['ContractCoreService', 'contract_core_service']
