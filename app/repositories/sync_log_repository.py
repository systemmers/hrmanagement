"""
SyncLog Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/sync/repositories/sync_log_repository.py 에 위치
"""
from app.domains.sync.repositories.sync_log_repository import (
    SyncLogRepository,
    sync_log_repository,
)

__all__ = [
    'SyncLogRepository',
    'sync_log_repository',
]
