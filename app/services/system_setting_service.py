"""
SystemSetting Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/platform/services/system_setting_service.py 에 위치
"""
from app.domains.platform.services.system_setting_service import (
    SystemSettingService,
    system_setting_service,
)

__all__ = [
    'SystemSettingService',
    'system_setting_service',
]
