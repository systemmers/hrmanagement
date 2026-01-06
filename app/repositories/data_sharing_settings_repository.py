"""
DataSharingSettings Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/data_sharing_settings_repository.py 에 위치
"""
from app.domains.company.repositories.data_sharing_settings_repository import (
    DataSharingSettingsRepository,
    data_sharing_settings_repository,
)

__all__ = [
    'DataSharingSettingsRepository',
    'data_sharing_settings_repository',
]
