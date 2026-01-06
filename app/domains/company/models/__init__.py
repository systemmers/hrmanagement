"""
Company Domain Models

Phase 5: 도메인 중심 마이그레이션
기존 모델을 re-export하여 점진적 마이그레이션 지원
"""

# 기존 모델에서 re-export (중복 정의 방지)
from app.models.company import Company
from app.models.company_settings import CompanySettings
from app.models.company_visibility_settings import CompanyVisibilitySettings
from app.models.company_document import CompanyDocument
from app.models.organization import Organization
from app.models.classification_option import ClassificationOption
from app.models.number_category import NumberCategory
from app.models.number_registry import NumberRegistry

__all__ = [
    'Company',
    'CompanySettings',
    'CompanyVisibilitySettings',
    'CompanyDocument',
    'Organization',
    'ClassificationOption',
    'NumberCategory',
    'NumberRegistry',
]
