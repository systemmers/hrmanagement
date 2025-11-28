"""
SQLAlchemy Repository 패키지

모든 Repository 클래스를 정의하고 export합니다.
기존 Blueprint 코드와의 호환성을 유지합니다.
"""
from .employee_repository import EmployeeRepository
from .classification_repository import ClassificationOptionsRepository
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
from .project_repository import ProjectRepository
from .award_repository import AwardRepository
from .asset_repository import AssetRepository
from .salary_payment_repository import SalaryPaymentRepository
from .attachment_repository import AttachmentRepository

__all__ = [
    'EmployeeRepository',
    'ClassificationOptionsRepository',
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
    'ProjectRepository',
    'AwardRepository',
    'AssetRepository',
    'SalaryPaymentRepository',
    'AttachmentRepository',
]
