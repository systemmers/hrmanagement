"""
Contract Service Package (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.services import contract_service
    from app.domains.contract.services import contract_core_service

Phase 2: 도메인 중심 마이그레이션 완료
- 실제 구현은 app/domains/contract/services/에 위치
- 이 파일은 하위 호환성을 위한 re-export
"""

# 도메인에서 re-export
from app.domains.contract.services import (
    ContractCoreService,
    ContractWorkflowService,
    ContractSettingsService,
    ContractFilterService,
    ContractService,
    contract_core_service,
    contract_workflow_service,
    contract_settings_service,
    contract_filter_service,
    contract_service,
)

__all__ = [
    'ContractService',
    'ContractCoreService',
    'ContractWorkflowService',
    'ContractSettingsService',
    'ContractFilterService',
    'contract_service',
    'contract_core_service',
    'contract_workflow_service',
    'contract_settings_service',
    'contract_filter_service',
]
