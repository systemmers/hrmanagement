"""
Sync Domain Services

개인(PersonalProfile) <-> 법인(Employee) 간 데이터 동기화 서비스

Phase 2: 도메인 중심 마이그레이션 완료
- 모든 Service가 도메인 내부에 위치
- 레거시 경로(app.services.sync)는 이 모듈을 re-export
"""

from .sync_service import SyncService
from .sync_basic_service import SyncBasicService
from .sync_relation_service import SyncRelationService
from .termination_service import TerminationService, termination_service

# Singleton instances
sync_service = SyncService()

__all__ = [
    # Classes
    'SyncService',
    'SyncBasicService',
    'SyncRelationService',
    'TerminationService',
    # Singleton instances
    'sync_service',
    'termination_service',
]
