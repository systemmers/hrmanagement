"""
Contract Service (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.services.contract import contract_service
    from app.services.contract import contract_core_service, contract_workflow_service

Phase 2: 구조화 - contract/ 폴더로 분리, 이 파일은 호환성 래퍼로 유지
"""

from app.services.contract import (
    ContractService,
    ContractCoreService,
    ContractWorkflowService,
    ContractSettingsService,
    contract_service,
    contract_core_service,
    contract_workflow_service,
    contract_settings_service,
)

__all__ = [
    'ContractService',
    'ContractCoreService',
    'ContractWorkflowService',
    'ContractSettingsService',
    'contract_service',
    'contract_core_service',
    'contract_workflow_service',
    'contract_settings_service',
]
