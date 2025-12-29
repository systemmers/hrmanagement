"""
Sync Service Package (Facade)

개인(PersonalProfile) <-> 법인(Employee) 간 데이터 동기화 서비스 패키지입니다.

기존 API 100% 호환성 유지:
    from app.services.sync_service import sync_service
    sync_service.sync_personal_to_employee(contract_id)

새로운 방식:
    from app.services.sync import sync_basic_service, sync_relation_service
    sync_basic_service.sync_personal_to_employee(...)

Phase 5: 구조화 - sync/ 폴더로 이동
"""

from .sync_basic_service import SyncBasicService
from .sync_relation_service import SyncRelationService
from .sync_service import SyncService, sync_service

__all__ = [
    'SyncService',
    'SyncBasicService',
    'SyncRelationService',
    'sync_service',
]
