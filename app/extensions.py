"""
저장소 초기화 모듈 (Extensions)

App Factory 패턴에서 저장소 인스턴스의 지연 초기화를 관리합니다.
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


def init_extensions(app):
    """앱 컨텍스트에서 저장소 초기화"""
    global employee_repo, classification_repo
    global education_repo, career_repo, certificate_repo
    global family_repo, language_repo, military_repo
    global salary_repo, benefit_repo, contract_repo, salary_history_repo
    global promotion_repo, evaluation_repo, training_repo, attendance_repo
    global insurance_repo, project_repo, award_repo, asset_repo
    global salary_payment_repo, attachment_repo

    from .models import (
        EmployeeRepository, ClassificationOptionsRepository,
        EducationRepository, CareerRepository, CertificateRepository,
        FamilyMemberRepository, LanguageRepository, MilitaryServiceRepository,
        SalaryRepository, BenefitRepository, ContractRepository, SalaryHistoryRepository,
        PromotionRepository, EvaluationRepository, TrainingRepository, AttendanceRepository,
        InsuranceRepository, ProjectRepository, AwardRepository, AssetRepository,
        SalaryPaymentRepository, AttachmentRepository
    )

    # 기본 저장소 초기화
    employee_repo = EmployeeRepository(
        app.config['EMPLOYEES_JSON'],
        app.config['EMPLOYEES_EXTENDED_JSON']
    )
    classification_repo = ClassificationOptionsRepository(
        app.config['CLASSIFICATION_OPTIONS_JSON']
    )

    # 관계형 데이터 저장소 초기화
    education_repo = EducationRepository(app.config['EDUCATION_JSON'])
    career_repo = CareerRepository(app.config['CAREERS_JSON'])
    certificate_repo = CertificateRepository(app.config['CERTIFICATES_JSON'])
    family_repo = FamilyMemberRepository(app.config['FAMILY_MEMBERS_JSON'])
    language_repo = LanguageRepository(app.config['LANGUAGES_JSON'])
    military_repo = MilitaryServiceRepository(app.config['MILITARY_JSON'])

    # Phase 2: 핵심 기능 저장소 초기화
    salary_repo = SalaryRepository(app.config['SALARIES_JSON'])
    benefit_repo = BenefitRepository(app.config['BENEFITS_JSON'])
    contract_repo = ContractRepository(app.config['CONTRACTS_JSON'])
    salary_history_repo = SalaryHistoryRepository(app.config['SALARY_HISTORY_JSON'])

    # Phase 3: 인사평가 기능 저장소 초기화
    promotion_repo = PromotionRepository(app.config['PROMOTIONS_JSON'])
    evaluation_repo = EvaluationRepository(app.config['EVALUATIONS_JSON'])
    training_repo = TrainingRepository(app.config['TRAININGS_JSON'])
    attendance_repo = AttendanceRepository(app.config['ATTENDANCE_JSON'])

    # Phase 4: 부가 기능 저장소 초기화
    insurance_repo = InsuranceRepository(app.config['INSURANCES_JSON'])
    project_repo = ProjectRepository(app.config['PROJECTS_JSON'])
    award_repo = AwardRepository(app.config['AWARDS_JSON'])
    asset_repo = AssetRepository(app.config['ASSETS_JSON'])

    # Phase 5: 급여 지급 이력 저장소 초기화
    salary_payment_repo = SalaryPaymentRepository(app.config['SALARY_PAYMENTS_JSON'])

    # Phase 6: 첨부파일 저장소 초기화
    attachment_repo = AttachmentRepository(app.config['ATTACHMENTS_JSON'])
