"""
Company Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/services/company_service.py 에 위치
"""
from app.domains.company.services.company_service import (
    CompanyService,
    company_service,
)

__all__ = [
    'CompanyService',
    'company_service',
]
