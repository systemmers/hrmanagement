"""
Platform Domain Services

Phase 7: 도메인 중심 마이그레이션 완료
"""
from .platform_service import PlatformService, platform_service
from .system_setting_service import SystemSettingService, system_setting_service
from .audit_service import AuditService, audit_service, audit_log

__all__ = [
    # Classes
    'PlatformService',
    'SystemSettingService',
    'AuditService',
    # Singleton instances
    'platform_service',
    'system_setting_service',
    'audit_service',
    # Decorators
    'audit_log',
]
