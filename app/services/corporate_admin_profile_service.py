"""
Corporate Admin Profile Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/user/services/corporate_admin_profile_service.py 에 위치
"""
from app.domains.user.services.corporate_admin_profile_service import (
    CorporateAdminProfileService,
    corporate_admin_profile_service,
)

__all__ = [
    'CorporateAdminProfileService',
    'corporate_admin_profile_service',
]
