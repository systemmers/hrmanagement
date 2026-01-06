"""
Company Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/company_repository.py 에 위치
"""
from app.domains.company.repositories.company_repository import (
    CompanyRepository,
    company_repository,
)

__all__ = [
    'CompanyRepository',
    'company_repository',
]
