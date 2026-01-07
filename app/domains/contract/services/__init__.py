"""
Contract Domain Services

계약 관련 비즈니스 로직 서비스

Phase 2: 도메인 중심 마이그레이션 완료
- 모든 Service가 도메인 내부에 위치
- 레거시 경로(app.services.contract)는 이 모듈을 re-export
"""

from .contract_core_service import ContractCoreService
from .contract_workflow_service import ContractWorkflowService
from .contract_settings_service import ContractSettingsService
from .contract_filter_service import ContractFilterService
from .contract_service import ContractService

# Singleton instances
contract_core_service = ContractCoreService()
contract_workflow_service = ContractWorkflowService()
contract_settings_service = ContractSettingsService()
contract_filter_service = ContractFilterService()
contract_service = ContractService()

__all__ = [
    # Classes
    'ContractCoreService',
    'ContractWorkflowService',
    'ContractSettingsService',
    'ContractFilterService',
    'ContractService',
    # Singleton instances
    'contract_core_service',
    'contract_workflow_service',
    'contract_settings_service',
    'contract_filter_service',
    'contract_service',
]
