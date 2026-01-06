"""
Company Domain Services

Phase 7: 도메인 중심 마이그레이션 완료
모든 Service가 도메인 내부에 구현됨

Note: CorporateAdminProfileService는 User 도메인으로 이동됨
"""

# 도메인 내부 Service에서 import
from .company_service import CompanyService, company_service
from .organization_service import OrganizationService, organization_service
from .corporate_settings_service import CorporateSettingsService, corporate_settings_service

__all__ = [
    # Classes
    'CompanyService',
    'OrganizationService',
    'CorporateSettingsService',
    # Singleton instances
    'company_service',
    'organization_service',
    'corporate_settings_service',
]
