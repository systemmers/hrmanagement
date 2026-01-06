"""
Personal Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/user/services/personal_service.py 에 위치
"""
from app.domains.user.services.personal_service import (
    PersonalService,
    personal_service,
)

__all__ = [
    'PersonalService',
    'personal_service',
]
