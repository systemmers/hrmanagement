"""
Classification Options Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/classification_repository.py 에 위치
"""
from app.domains.company.repositories.classification_repository import (
    ClassificationOptionsRepository,
    classification_repository,
)

__all__ = [
    'ClassificationOptionsRepository',
    'classification_repository',
]
