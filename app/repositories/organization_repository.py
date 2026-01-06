"""
Organization Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/organization_repository.py 에 위치
"""
from app.domains.company.repositories.organization_repository import (
    OrganizationRepository,
    organization_repository,
)

__all__ = [
    'OrganizationRepository',
    'organization_repository',
]
