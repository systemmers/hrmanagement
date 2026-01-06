"""
SystemSetting Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/platform/repositories/system_setting_repository.py 에 위치
"""
from app.domains.platform.repositories.system_setting_repository import (
    SystemSettingRepository,
    system_setting_repository,
)

__all__ = [
    'SystemSettingRepository',
    'system_setting_repository',
]
