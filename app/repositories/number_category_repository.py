"""
Number Category Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/number_category_repository.py 에 위치
"""
from app.domains.company.repositories.number_category_repository import (
    NumberCategoryRepository,
    number_category_repository,
)

__all__ = [
    'NumberCategoryRepository',
    'number_category_repository',
]
