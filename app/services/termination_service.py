"""
퇴사 처리 서비스 - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/sync/services/termination_service.py 에 위치
"""
from app.domains.sync.services.termination_service import (
    TerminationService,
    termination_service,
)

__all__ = [
    'TerminationService',
    'termination_service',
]
