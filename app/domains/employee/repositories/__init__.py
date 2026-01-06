# app/domains/employee/repositories/__init__.py
"""
Employee 도메인 Repository 패키지

직원 관련 모든 Repository를 정의하고 export합니다.
"""
from .employee_repository import EmployeeRepository
from .profile_repository import ProfileRepository
from .education_repository import EducationRepository
from .career_repository import CareerRepository
from .certificate_repository import CertificateRepository
from .family_member_repository import FamilyMemberRepository
from .language_repository import LanguageRepository
from .military_service_repository import MilitaryServiceRepository
from .salary_repository import SalaryRepository
from .benefit_repository import BenefitRepository
from .contract_repository import ContractRepository
from .salary_history_repository import SalaryHistoryRepository
from .promotion_repository import PromotionRepository
from .evaluation_repository import EvaluationRepository
from .training_repository import TrainingRepository
from .attendance_repository import AttendanceRepository
from .insurance_repository import InsuranceRepository
from .hr_project_repository import HrProjectRepository
from .project_participation_repository import ProjectParticipationRepository
from .award_repository import AwardRepository
from .asset_repository import AssetRepository
from .salary_payment_repository import SalaryPaymentRepository
from .attachment_repository import AttachmentRepository


__all__ = [
    # Core
    'EmployeeRepository',
    'ProfileRepository',
    # 1:N Relations
    'EducationRepository',
    'CareerRepository',
    'CertificateRepository',
    'FamilyMemberRepository',
    'LanguageRepository',
    'SalaryHistoryRepository',
    'PromotionRepository',
    'EvaluationRepository',
    'TrainingRepository',
    'AttendanceRepository',
    'HrProjectRepository',
    'ProjectParticipationRepository',
    'AwardRepository',
    'AssetRepository',
    'SalaryPaymentRepository',
    'AttachmentRepository',
    # 1:1 Relations
    'MilitaryServiceRepository',
    'SalaryRepository',
    'BenefitRepository',
    'ContractRepository',
    'InsuranceRepository',
]
