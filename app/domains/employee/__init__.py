# app/domains/employee/__init__.py
"""
직원 도메인 패키지

직원 관련 모든 기능을 포함합니다:
- 직원 CRUD
- 직원 관계형 데이터 (학력, 경력, 자격증 등)

Phase 31: Attachment는 독립 도메인으로 분리됨 (app/domains/attachment/)
"""

# Repository 인스턴스 (지연 초기화)
_employee_repo = None
_education_repo = None
_career_repo = None
_certificate_repo = None
_family_member_repo = None
_language_repo = None
_military_service_repo = None
_salary_repo = None
_benefit_repo = None
_contract_repo = None
_salary_history_repo = None
_promotion_repo = None
_evaluation_repo = None
_training_repo = None
_attendance_repo = None
_insurance_repo = None
_hr_project_repo = None
_project_participation_repo = None
_award_repo = None
_asset_repo = None
_salary_payment_repo = None
_profile_repo = None


def init_repositories():
    """도메인 Repository 초기화"""
    global _employee_repo
    global _education_repo, _career_repo, _certificate_repo
    global _family_member_repo, _language_repo, _military_service_repo
    global _salary_repo, _benefit_repo, _contract_repo, _salary_history_repo
    global _promotion_repo, _evaluation_repo, _training_repo, _attendance_repo
    global _insurance_repo, _hr_project_repo, _project_participation_repo
    global _award_repo, _asset_repo, _salary_payment_repo
    global _profile_repo

    from .repositories import (
        EmployeeRepository,
        EducationRepository, CareerRepository, CertificateRepository,
        FamilyMemberRepository, LanguageRepository, MilitaryServiceRepository,
        SalaryRepository, BenefitRepository, ContractRepository, SalaryHistoryRepository,
        PromotionRepository, EvaluationRepository, TrainingRepository, AttendanceRepository,
        InsuranceRepository, HrProjectRepository, ProjectParticipationRepository,
        AwardRepository, AssetRepository, SalaryPaymentRepository,
        ProfileRepository
    )

    _employee_repo = EmployeeRepository()
    _education_repo = EducationRepository()
    _career_repo = CareerRepository()
    _certificate_repo = CertificateRepository()
    _family_member_repo = FamilyMemberRepository()
    _language_repo = LanguageRepository()
    _military_service_repo = MilitaryServiceRepository()
    _salary_repo = SalaryRepository()
    _benefit_repo = BenefitRepository()
    _contract_repo = ContractRepository()
    _salary_history_repo = SalaryHistoryRepository()
    _promotion_repo = PromotionRepository()
    _evaluation_repo = EvaluationRepository()
    _training_repo = TrainingRepository()
    _attendance_repo = AttendanceRepository()
    _insurance_repo = InsuranceRepository()
    _hr_project_repo = HrProjectRepository()
    _project_participation_repo = ProjectParticipationRepository()
    _award_repo = AwardRepository()
    _asset_repo = AssetRepository()
    _salary_payment_repo = SalaryPaymentRepository()
    _profile_repo = ProfileRepository()


def get_employee_repo():
    return _employee_repo


def get_education_repo():
    return _education_repo


def get_career_repo():
    return _career_repo


def get_certificate_repo():
    return _certificate_repo


def get_family_member_repo():
    return _family_member_repo


def get_language_repo():
    return _language_repo


def get_military_service_repo():
    return _military_service_repo


def get_classification_repo():
    return _classification_repo


def get_salary_repo():
    return _salary_repo


def get_benefit_repo():
    return _benefit_repo


def get_contract_repo():
    return _contract_repo


def get_salary_history_repo():
    return _salary_history_repo


def get_promotion_repo():
    return _promotion_repo


def get_evaluation_repo():
    return _evaluation_repo


def get_training_repo():
    return _training_repo


def get_attendance_repo():
    return _attendance_repo


def get_insurance_repo():
    return _insurance_repo


def get_hr_project_repo():
    return _hr_project_repo


def get_project_participation_repo():
    return _project_participation_repo


def get_award_repo():
    return _award_repo


def get_asset_repo():
    return _asset_repo


def get_salary_payment_repo():
    return _salary_payment_repo


def get_profile_repo():
    return _profile_repo
