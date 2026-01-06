"""
Company Domain

법인 관련 모든 기능을 포함합니다:
- Models: Company, CompanySettings, CompanyVisibilitySettings, CompanyDocument, Organization, ClassificationOption, NumberCategory, NumberRegistry
- Repositories: CompanyRepository, CompanySettingsRepository, CompanyVisibilityRepository, CompanyDocumentRepository, OrganizationRepository, ClassificationOptionsRepository, NumberCategoryRepository, DataSharingSettingsRepository
- Services: CompanyService, OrganizationService, CorporateSettingsService

Phase 7: 도메인 중심 마이그레이션 완료

Note: CorporateAdminProfileService는 User 도메인으로 이동됨
"""

# Repository 인스턴스 (지연 초기화)
_company_repo = None
_organization_repo = None
_company_settings_repo = None
_company_visibility_repo = None
_company_document_repo = None
_classification_repo = None
_number_category_repo = None
_data_sharing_settings_repo = None

# Service 인스턴스 (지연 초기화)
_company_service = None
_organization_service = None
_corporate_settings_service = None


def init_repositories():
    """도메인 Repository 초기화

    extensions.py에서 호출됩니다.
    """
    global _company_repo, _organization_repo, _company_settings_repo
    global _company_visibility_repo, _company_document_repo
    global _classification_repo, _number_category_repo, _data_sharing_settings_repo

    from .repositories import (
        CompanyRepository,
        OrganizationRepository,
        CompanySettingsRepository,
        CompanyVisibilityRepository,
        CompanyDocumentRepository,
        ClassificationOptionsRepository,
        NumberCategoryRepository,
        DataSharingSettingsRepository,
    )

    _company_repo = CompanyRepository()
    _organization_repo = OrganizationRepository()
    _company_settings_repo = CompanySettingsRepository()
    _company_visibility_repo = CompanyVisibilityRepository()
    _company_document_repo = CompanyDocumentRepository()
    _classification_repo = ClassificationOptionsRepository()
    _number_category_repo = NumberCategoryRepository()
    _data_sharing_settings_repo = DataSharingSettingsRepository()


def init_services():
    """도메인 Service 초기화

    extensions.py에서 호출됩니다.
    """
    global _company_service, _organization_service, _corporate_settings_service

    from .services import (
        CompanyService,
        OrganizationService,
        CorporateSettingsService,
    )

    _company_service = CompanyService()
    _organization_service = OrganizationService()
    _corporate_settings_service = CorporateSettingsService()


# ========================================
# Repository Getters
# ========================================

def get_company_repo():
    """CompanyRepository 인스턴스 반환"""
    return _company_repo


def get_organization_repo():
    """OrganizationRepository 인스턴스 반환"""
    return _organization_repo


def get_company_settings_repo():
    """CompanySettingsRepository 인스턴스 반환"""
    return _company_settings_repo


def get_company_visibility_repo():
    """CompanyVisibilityRepository 인스턴스 반환"""
    return _company_visibility_repo


def get_company_document_repo():
    """CompanyDocumentRepository 인스턴스 반환"""
    return _company_document_repo


def get_classification_repo():
    """ClassificationOptionsRepository 인스턴스 반환"""
    return _classification_repo


def get_number_category_repo():
    """NumberCategoryRepository 인스턴스 반환"""
    return _number_category_repo


def get_data_sharing_settings_repo():
    """DataSharingSettingsRepository 인스턴스 반환"""
    return _data_sharing_settings_repo


# ========================================
# Service Getters
# ========================================

def get_company_service():
    """CompanyService 인스턴스 반환"""
    return _company_service


def get_organization_service():
    """OrganizationService 인스턴스 반환"""
    return _organization_service


def get_corporate_settings_service():
    """CorporateSettingsService 인스턴스 반환"""
    return _corporate_settings_service


# 외부 인터페이스
__all__ = [
    # Functions - Initialization
    'init_repositories',
    'init_services',
    # Functions - Repository Getters
    'get_company_repo',
    'get_organization_repo',
    'get_company_settings_repo',
    'get_company_visibility_repo',
    'get_company_document_repo',
    'get_classification_repo',
    'get_number_category_repo',
    'get_data_sharing_settings_repo',
    # Functions - Service Getters
    'get_company_service',
    'get_organization_service',
    'get_corporate_settings_service',
]
