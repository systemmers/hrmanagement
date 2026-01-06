"""
PersonCorporateContract, DataSharingSettings, SyncLog (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.models import PersonCorporateContract, DataSharingSettings, SyncLog

Phase 5: 구조화 - person_contract_pkg/ 폴더로 분리
Phase 2 Migration: 도메인으로 이동, 이 파일은 호환성 래퍼로 유지
"""

# 도메인에서 re-export (Phase 2 Migration)
from app.domains.contract.models import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog,
)

__all__ = [
    'PersonCorporateContract',
    'DataSharingSettings',
    'SyncLog',
]
