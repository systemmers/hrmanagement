"""
Person Contract Models Package

개인-법인 간 계약 관계 관련 모델 패키지입니다.

기존 API 100% 호환성 유지:
    from app.models.person_contract import PersonCorporateContract, DataSharingSettings, SyncLog

새로운 방식:
    from app.models.person_contract_pkg import PersonCorporateContract, DataSharingSettings, SyncLog

Phase 5: 구조화 - person_contract_pkg/ 폴더로 분리
(contract/ 이름은 기존 Contract(HR 계약) 모델과 충돌하므로 person_contract_pkg로 명명)
"""

from .person_contract import PersonCorporateContract
from .data_sharing_settings import DataSharingSettings
from .sync_log import SyncLog

__all__ = [
    'PersonCorporateContract',
    'DataSharingSettings',
    'SyncLog',
]
