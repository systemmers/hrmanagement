"""
Person Contract Models Package

개인-법인 간 계약 관계 관련 모델 패키지입니다.

[DEPRECATED] 레거시 호환성 래퍼
새 코드는 다음을 사용하세요:
    from app.domains.contract.models import PersonCorporateContract, DataSharingSettings, SyncLog

Phase 5: 구조화 - person_contract_pkg/ 폴더로 분리
Phase 2 Migration: 도메인으로 이동, 이 파일은 re-export 래퍼로 유지
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
