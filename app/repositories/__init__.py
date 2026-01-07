"""
SQLAlchemy Repository 패키지

모든 Repository 클래스를 정의하고 export합니다.
기존 Blueprint 코드와의 호환성을 유지합니다.

Phase 3: Employee 도메인 Repository는 app.domains.employee.repositories로 이동됨
         순환 참조 방지를 위해 __getattr__로 지연 import 구현
Phase 8: 미사용 래퍼 파일 삭제
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


def __getattr__(name):
    """Employee 도메인 Repository 지연 import (순환 참조 방지)"""
    if name in _EMPLOYEE_DOMAIN_REPOS:
        from app.domains.employee import repositories as emp_repos
        return getattr(emp_repos, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Company Domain Repositories (사용 중인 래퍼만 유지)
from .company_repository import CompanyRepository
from .organization_repository import OrganizationRepository

# User Domain Repositories (사용 중인 래퍼만 유지)
from .user_repository import UserRepository

# Contract Domain Repositories
# from .person_contract_repository import PersonContractRepository  # 특수 처리


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
    # User Domain
    'UserRepository',
]
