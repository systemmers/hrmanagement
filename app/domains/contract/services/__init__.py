"""
Contract Domain Services

Phase 4: 도메인 중심 마이그레이션
기존 Service를 re-export하여 점진적 마이그레이션 지원
"""

# Contract Facade 서비스 (기존 contract/ 폴더)
from app.services.contract import (
    ContractCoreService,
    ContractWorkflowService,
    ContractSettingsService,
    contract_core_service,
    contract_workflow_service,
    contract_settings_service,
)

# Contract 통합 서비스 (기존 contract_service.py)
from app.services.contract_service import ContractService, contract_service

# Contract Filter 서비스 (별도 파일)
from app.services.contract_filter_service import ContractFilterService, contract_filter_service

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
