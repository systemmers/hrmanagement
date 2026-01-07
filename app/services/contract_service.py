"""
Contract Service (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.services import contract_service

Phase 2: 도메인 중심 마이그레이션 완료
"""

from app.domains.contract.services import (
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
