"""
Sync Domain

동기화 관련 모든 기능을 포함합니다:
- Repositories: SyncLogRepository
- Services: SyncService, SyncBasicService, SyncRelationService, TerminationService
- Blueprints: sync_bp

Phase 7: 도메인 중심 마이그레이션 완료
"""

# Repository 인스턴스 (지연 초기화)
_sync_log_repo = None

# Service 인스턴스 (지연 초기화)
_termination_service = None


def init_repositories():
    """도메인 Repository 초기화

    extensions.py에서 호출됩니다.
    """
    global _sync_log_repo

    from .repositories import SyncLogRepository

    _sync_log_repo = SyncLogRepository()


def init_services():
    """도메인 Service 초기화

    extensions.py에서 호출됩니다.
    """
    global _termination_service

    from .services import TerminationService

    _termination_service = TerminationService()


# Repository Getters
def get_sync_log_repo():
    """SyncLogRepository 인스턴스 반환"""
    return _sync_log_repo


# Service Getters
def get_termination_service():
    """TerminationService 인스턴스 반환"""
    return _termination_service


# 외부 인터페이스
__all__ = [
    # Functions
    'init_repositories',
    'init_services',
    'get_sync_log_repo',
    'get_termination_service',
]
