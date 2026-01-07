"""
Contract Settings Service (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.services import ContractSettingsService
"""
from app.domains.contract.services.contract_settings_service import ContractSettingsService

contract_settings_service = ContractSettingsService()

__all__ = ['ContractSettingsService', 'contract_settings_service']
