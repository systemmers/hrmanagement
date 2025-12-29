"""
PersonCorporateContract, DataSharingSettings, SyncLog (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.models.person_contract_pkg import PersonCorporateContract, DataSharingSettings, SyncLog

Phase 5: 구조화 - person_contract_pkg/ 폴더로 분리, 이 파일은 호환성 래퍼로 유지
(contract/ 이름은 기존 Contract(HR 계약) 모델과 충돌하므로 person_contract_pkg로 명명)
"""

from app.models.person_contract_pkg import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog,
)

__all__ = [
    'PersonCorporateContract',
    'DataSharingSettings',
    'SyncLog',
]
