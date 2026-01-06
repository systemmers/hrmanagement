"""
User Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/user/services/user_service.py 에 위치
"""
from app.domains.user.services.user_service import (
    UserService,
    user_service,
)

__all__ = [
    'UserService',
    'user_service',
]
