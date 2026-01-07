"""
Contract Filter Service (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.services import contract_filter_service

Phase 2: 도메인 중심 마이그레이션 완료
"""

from app.domains.contract.services import (
    ContractFilterService,
    contract_filter_service,
)

__all__ = [
    'ContractFilterService',
    'contract_filter_service',
]
