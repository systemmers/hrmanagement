"""
Organization Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/services/organization_service.py 에 위치
"""
from app.domains.company.services.organization_service import (
    OrganizationService,
    organization_service,
)

__all__ = [
    'OrganizationService',
    'organization_service',
]
