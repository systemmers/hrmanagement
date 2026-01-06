"""
SQLAlchemy 이벤트 리스너 - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/shared/services/event_listeners.py 에 위치
"""
from app.shared.services.event_listeners import (
    SyncEventManager,
    ContractEventManager,
    init_event_listeners,
    cleanup_event_listeners,
    get_model_changes,
    track_field_changes,
)

__all__ = [
    'SyncEventManager',
    'ContractEventManager',
    'init_event_listeners',
    'cleanup_event_listeners',
    'get_model_changes',
    'track_field_changes',
]
