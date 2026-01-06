"""
Contract Domain Models

Phase 4: 도메인 중심 마이그레이션
기존 모델을 re-export하여 점진적 마이그레이션 지원
"""

# 기존 모델에서 re-export (중복 정의 방지)
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
