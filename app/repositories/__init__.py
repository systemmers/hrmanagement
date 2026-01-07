"""
SQLAlchemy Repository 패키지

모든 Repository 클래스를 정의하고 export합니다.
기존 Blueprint 코드와의 호환성을 유지합니다.

Phase 3: Employee 도메인 Repository는 app.domains.employee.repositories로 이동됨
         순환 참조 방지를 위해 __getattr__로 지연 import 구현
Phase 8: 모든 도메인 Repository가 app.domains/로 마이그레이션됨
"""

# Employee 도메인 Repository 이름 목록 (지연 import 대상)
_EMPLOYEE_DOMAIN_REPOS = {
    'EmployeeRepository',
    'ProfileRepository',
    'EducationRepository',
    'CareerRepository',
    'CertificateRepository',
    'FamilyMemberRepository',
    'LanguageRepository',
    'MilitaryServiceRepository',
    'SalaryRepository',
    'BenefitRepository',
    'ContractRepository',
    'SalaryHistoryRepository',
    'PromotionRepository',
    'EvaluationRepository',
    'TrainingRepository',
    'AttendanceRepository',
    'InsuranceRepository',
    'HrProjectRepository',
    'ProjectParticipationRepository',
    'AwardRepository',
    'AssetRepository',
    'SalaryPaymentRepository',
    'AttachmentRepository',
}

# Company Domain Repositories
_COMPANY_DOMAIN_REPOS = {
    'CompanyRepository',
    'OrganizationRepository',
    'ClassificationRepository',
    'CompanySettingsRepository',
    'CompanyDocumentRepository',
    'CompanyVisibilityRepository',
    'NumberCategoryRepository',
    'DataSharingSettingsRepository',
}

# User Domain Repositories
_USER_DOMAIN_REPOS = {
    'UserRepository',
    'CorporateAdminProfileRepository',
    'NotificationRepository',
    'PersonalProfileRepository',
}

# Contract Domain Repositories
_CONTRACT_DOMAIN_REPOS = {
    'PersonContractRepository',
}

# Sync Domain Repositories
_SYNC_DOMAIN_REPOS = {
    'SyncLogRepository',
}

# Platform Domain Repositories
_PLATFORM_DOMAIN_REPOS = {
    'AuditLogRepository',
    'SystemSettingRepository',
}


def __getattr__(name):
    """도메인 Repository 지연 import (순환 참조 방지)"""
    if name in _EMPLOYEE_DOMAIN_REPOS:
        from app.domains.employee import repositories as emp_repos
        return getattr(emp_repos, name)
    if name in _COMPANY_DOMAIN_REPOS:
        from app.domains.company import repositories as company_repos
        return getattr(company_repos, name)
    if name in _USER_DOMAIN_REPOS:
        from app.domains.user import repositories as user_repos
        return getattr(user_repos, name)
    if name in _CONTRACT_DOMAIN_REPOS:
        from app.domains.contract import repositories as contract_repos
        return getattr(contract_repos, name)
    if name in _SYNC_DOMAIN_REPOS:
        from app.domains.sync import repositories as sync_repos
        return getattr(sync_repos, name)
    if name in _PLATFORM_DOMAIN_REPOS:
        from app.domains.platform import repositories as platform_repos
        return getattr(platform_repos, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Employee Domain
    'EmployeeRepository',
    'ProfileRepository',
    'EducationRepository',
    'CareerRepository',
    'CertificateRepository',
    'FamilyMemberRepository',
    'LanguageRepository',
    'MilitaryServiceRepository',
    'SalaryRepository',
    'BenefitRepository',
    'ContractRepository',
    'SalaryHistoryRepository',
    'PromotionRepository',
    'EvaluationRepository',
    'TrainingRepository',
    'AttendanceRepository',
    'InsuranceRepository',
    'HrProjectRepository',
    'ProjectParticipationRepository',
    'AwardRepository',
    'AssetRepository',
    'SalaryPaymentRepository',
    'AttachmentRepository',
    # Company Domain
    'CompanyRepository',
    'OrganizationRepository',
    'ClassificationRepository',
    'CompanySettingsRepository',
    'CompanyDocumentRepository',
    'CompanyVisibilityRepository',
    'NumberCategoryRepository',
    'DataSharingSettingsRepository',
    # User Domain
    'UserRepository',
    'CorporateAdminProfileRepository',
    'NotificationRepository',
    'PersonalProfileRepository',
    # Contract Domain
    'PersonContractRepository',
    # Sync Domain
    'SyncLogRepository',
    # Platform Domain
    'AuditLogRepository',
    'SystemSettingRepository',
]
