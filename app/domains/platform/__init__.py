"""
Platform Domain

플랫폼 관리 관련 모든 기능을 포함합니다:
- Models: SystemSetting, AuditLog
- Repositories: SystemSettingRepository, AuditLogRepository
- Services: PlatformService, SystemSettingService, AuditService
- Blueprints: platform_bp

Phase 7: 도메인 중심 마이그레이션 완료
"""

# Repository 인스턴스 (지연 초기화)
_system_setting_repo = None
_audit_log_repo = None

# Service 인스턴스 (지연 초기화)
_platform_service = None
_system_setting_service = None
_audit_service = None


def init_repositories():
    """도메인 Repository 초기화

    extensions.py에서 호출됩니다.
    """
    global _system_setting_repo, _audit_log_repo

    from .repositories import SystemSettingRepository, AuditLogRepository

    _system_setting_repo = SystemSettingRepository()
    _audit_log_repo = AuditLogRepository()


def init_services():
    """도메인 Service 초기화

    extensions.py에서 호출됩니다.
    """
    global _platform_service, _system_setting_service, _audit_service

    from .services import PlatformService, SystemSettingService, AuditService

    _platform_service = PlatformService()
    _system_setting_service = SystemSettingService()
    _audit_service = AuditService()


# Repository Getters
def get_system_setting_repo():
    """SystemSettingRepository 인스턴스 반환"""
    return _system_setting_repo


def get_audit_log_repo():
    """AuditLogRepository 인스턴스 반환"""
    return _audit_log_repo


# Service Getters
def get_platform_service():
    """PlatformService 인스턴스 반환"""
    return _platform_service


def get_system_setting_service():
    """SystemSettingService 인스턴스 반환"""
    return _system_setting_service


def get_audit_service():
    """AuditService 인스턴스 반환"""
    return _audit_service


# 외부 인터페이스
__all__ = [
    # Functions
    'init_repositories',
    'init_services',
    'get_system_setting_repo',
    'get_audit_log_repo',
    'get_platform_service',
    'get_system_setting_service',
    'get_audit_service',
]
