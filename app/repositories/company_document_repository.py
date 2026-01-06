"""
Company Document Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/company_document_repository.py 에 위치
"""
from app.domains.company.repositories.company_document_repository import (
    CompanyDocumentRepository,
    company_document_repository,
)

__all__ = [
    'CompanyDocumentRepository',
    'company_document_repository',
]
