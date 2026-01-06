"""
Company Visibility Settings Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/company_visibility_repository.py 에 위치
"""
from app.domains.company.repositories.company_visibility_repository import (
    CompanyVisibilityRepository,
    company_visibility_repository,
)

__all__ = [
    'CompanyVisibilityRepository',
    'company_visibility_repository',
]
