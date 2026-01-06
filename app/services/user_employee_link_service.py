"""
User-Employee Link Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/user/services/user_employee_link_service.py 에 위치
"""
from app.domains.user.services.user_employee_link_service import (
    UserEmployeeLinkService,
    user_employee_link_service,
)

__all__ = [
    'UserEmployeeLinkService',
    'user_employee_link_service',
]
