"""
저장소 초기화 모듈 (Extensions)

App Factory 패턴에서 저장소 인스턴스의 지연 초기화를 관리합니다.
SQLAlchemy 기반 Repository를 사용합니다.
"""

# 저장소 인스턴스 (지연 초기화)
# 기본 저장소
employee_repo = None
classification_repo = None

# 관계형 데이터 저장소
education_repo = None
career_repo = None
certificate_repo = None
family_repo = None
language_repo = None
military_repo = None

# Phase 2: 핵심 기능 저장소
salary_repo = None
benefit_repo = None
contract_repo = None
salary_history_repo = None

# Phase 3: 인사평가 기능 저장소
promotion_repo = None
evaluation_repo = None
training_repo = None
attendance_repo = None

# Phase 4: 부가 기능 저장소
insurance_repo = None
project_repo = None
award_repo = None
asset_repo = None

# Phase 5: 급여 지급 이력 저장소
salary_payment_repo = None

# Phase 6: 첨부파일 저장소
attachment_repo = None

# Phase 1-1: 사용자 인증 저장소
user_repo = None

# Phase 1-5: 조직 구조 저장소
organization_repo = None

# Phase 1-9: 시스템 설정 저장소
system_setting_repo = None


def init_extensions(app):
    """앱 컨텍스트에서 저장소 초기화"""
    global employee_repo, classification_repo
    global education_repo, career_repo, certificate_repo
    global family_repo, language_repo, military_repo
    global salary_repo, benefit_repo, contract_repo, salary_history_repo
    global promotion_repo, evaluation_repo, training_repo, attendance_repo
    global insurance_repo, project_repo, award_repo, asset_repo
    global salary_payment_repo, attachment_repo
    global user_repo, organization_repo, system_setting_repo

    # SQLAlchemy 기반 Repository import
    from .repositories import (
        EmployeeRepository, ClassificationOptionsRepository,
        EducationRepository, CareerRepository, CertificateRepository,
        FamilyMemberRepository, LanguageRepository, MilitaryServiceRepository,
        SalaryRepository, BenefitRepository, ContractRepository, SalaryHistoryRepository,
        PromotionRepository, EvaluationRepository, TrainingRepository, AttendanceRepository,
        InsuranceRepository, ProjectRepository, AwardRepository, AssetRepository,
        SalaryPaymentRepository, AttachmentRepository
    )

    # 기본 저장소 초기화 (SQLAlchemy 기반 - JSON 경로 불필요)
    employee_repo = EmployeeRepository()
    classification_repo = ClassificationOptionsRepository()

    # 관계형 데이터 저장소 초기화
    education_repo = EducationRepository()
    career_repo = CareerRepository()
    certificate_repo = CertificateRepository()
    family_repo = FamilyMemberRepository()
    language_repo = LanguageRepository()
    military_repo = MilitaryServiceRepository()

    # Phase 2: 핵심 기능 저장소 초기화
    salary_repo = SalaryRepository()
    benefit_repo = BenefitRepository()
    contract_repo = ContractRepository()
    salary_history_repo = SalaryHistoryRepository()

    # Phase 3: 인사평가 기능 저장소 초기화
    promotion_repo = PromotionRepository()
    evaluation_repo = EvaluationRepository()
    training_repo = TrainingRepository()
    attendance_repo = AttendanceRepository()

    # Phase 4: 부가 기능 저장소 초기화
    insurance_repo = InsuranceRepository()
    project_repo = ProjectRepository()
    award_repo = AwardRepository()
    asset_repo = AssetRepository()

    # Phase 5: 급여 지급 이력 저장소 초기화
    salary_payment_repo = SalaryPaymentRepository()

    # Phase 6: 첨부파일 저장소 초기화
    attachment_repo = AttachmentRepository()

    # Phase 1-1: 사용자 인증 저장소 초기화
    from .repositories.user_repository import UserRepository
    user_repo = UserRepository()

    # Phase 1-5: 조직 구조 저장소 초기화
    from .repositories.organization_repository import OrganizationRepository
    organization_repo = OrganizationRepository()

    # Phase 1-9: 시스템 설정 저장소 초기화
    from .repositories.system_setting_repository import SystemSettingRepository
    system_setting_repo = SystemSettingRepository()
