"""
Company Domain Repositories

Phase 7: 도메인 중심 마이그레이션 완료
모든 Repository가 도메인 내부에 구현됨
"""

# 도메인 내부 Repository에서 import
from .company_repository import CompanyRepository, company_repository
from .company_settings_repository import CompanySettingsRepository, company_settings_repository
from .company_visibility_repository import CompanyVisibilityRepository, company_visibility_repository
from .company_document_repository import CompanyDocumentRepository, company_document_repository
from .organization_repository import OrganizationRepository, organization_repository
from .classification_repository import ClassificationOptionsRepository, classification_repository
from .number_category_repository import NumberCategoryRepository, number_category_repository
from .data_sharing_settings_repository import DataSharingSettingsRepository, data_sharing_settings_repository
from .organization_type_config_repository import OrganizationTypeConfigRepository, organization_type_config_repository

__all__ = [
    # Classes
    'CompanyRepository',
    'CompanySettingsRepository',
    'CompanyVisibilityRepository',
    'CompanyDocumentRepository',
    'OrganizationRepository',
    'ClassificationOptionsRepository',
    'NumberCategoryRepository',
    'DataSharingSettingsRepository',
    'OrganizationTypeConfigRepository',
    # Singleton instances
    'company_repository',
    'company_settings_repository',
    'company_visibility_repository',
    'company_document_repository',
    'organization_repository',
    'classification_repository',
    'number_category_repository',
    'data_sharing_settings_repository',
    'organization_type_config_repository',
]
