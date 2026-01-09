"""
저장소 초기화 모듈 (Extensions)

App Factory 패턴에서 저장소 인스턴스의 지연 초기화를 관리합니다.
SQLAlchemy 기반 Repository를 사용합니다.

Phase 8: 도메인 중심 마이그레이션 - 도메인별 init_repositories() 호출
"""
from flask_wtf.csrf import CSRFProtect

# CSRF 보호 인스턴스
csrf = CSRFProtect()

# ============================================================
# 하위 호환성을 위한 전역 변수
# (기존 코드에서 extensions.employee_repo 등으로 접근하는 경우 지원)
# ============================================================

# Employee 도메인 Repository
employee_repo = None
education_repo = None
career_repo = None
certificate_repo = None
family_repo = None
language_repo = None
military_repo = None
salary_repo = None
benefit_repo = None
contract_repo = None
salary_history_repo = None
promotion_repo = None
evaluation_repo = None
training_repo = None
attendance_repo = None
insurance_repo = None
hr_project_repo = None
project_participation_repo = None
award_repo = None
asset_repo = None
salary_payment_repo = None
attachment_repo = None

# Contract 도메인 Repository
person_contract_repo = None

# Company 도메인 Repository
classification_repo = None
organization_repo = None

# User 도메인 Repository
user_repo = None
notification_repo = None
notification_preference_repo = None

# Platform 도메인 Repository
system_setting_repo = None
audit_log_repo = None

# 레거시 Repository (도메인 마이그레이션 대기)
sync_log_repo = None


def init_extensions(app):
    """앱 컨텍스트에서 저장소 초기화

    각 도메인의 init_repositories()를 호출하고,
    하위 호환성을 위해 전역 변수에 할당합니다.
    """
    global employee_repo, classification_repo, organization_repo
    global education_repo, career_repo, certificate_repo
    global family_repo, language_repo, military_repo
    global salary_repo, benefit_repo, contract_repo, salary_history_repo
    global promotion_repo, evaluation_repo, training_repo, attendance_repo
    global insurance_repo, hr_project_repo, project_participation_repo, award_repo, asset_repo
    global salary_payment_repo, attachment_repo
    global user_repo, system_setting_repo, audit_log_repo
    global person_contract_repo
    global sync_log_repo
    global notification_repo, notification_preference_repo

    # CSRF 보호 초기화
    csrf.init_app(app)

    # ============================================================
    # 도메인별 Repository 초기화
    # ============================================================

    # 1. Employee 도메인
    from app.domains.employee import init_repositories as init_employee_repos
    from app.domains import employee as employee_domain
    init_employee_repos()

    # Employee 도메인 전역 변수 할당 (하위 호환성)
    employee_repo = employee_domain.get_employee_repo()
    education_repo = employee_domain.get_education_repo()
    career_repo = employee_domain.get_career_repo()
    certificate_repo = employee_domain.get_certificate_repo()
    family_repo = employee_domain.get_family_member_repo()
    language_repo = employee_domain.get_language_repo()
    military_repo = employee_domain.get_military_service_repo()
    salary_repo = employee_domain.get_salary_repo()
    benefit_repo = employee_domain.get_benefit_repo()
    contract_repo = employee_domain.get_contract_repo()
    salary_history_repo = employee_domain.get_salary_history_repo()
    promotion_repo = employee_domain.get_promotion_repo()
    evaluation_repo = employee_domain.get_evaluation_repo()
    training_repo = employee_domain.get_training_repo()
    attendance_repo = employee_domain.get_attendance_repo()
    insurance_repo = employee_domain.get_insurance_repo()
    hr_project_repo = employee_domain.get_hr_project_repo()
    project_participation_repo = employee_domain.get_project_participation_repo()
    award_repo = employee_domain.get_award_repo()
    asset_repo = employee_domain.get_asset_repo()
    salary_payment_repo = employee_domain.get_salary_payment_repo()

    # 1.5. Attachment 도메인 (Phase 31: employee에서 분리)
    from app.domains.attachment import init_repositories as init_attachment_repos
    from app.domains import attachment as attachment_domain
    init_attachment_repos()

    # Attachment 도메인 전역 변수 할당 (하위 호환성)
    attachment_repo = attachment_domain.get_attachment_repo()

    # 2. Contract 도메인
    from app.domains.contract import init_repositories as init_contract_repos
    from app.domains import contract as contract_domain
    init_contract_repos()

    # Contract 도메인 전역 변수 할당 (하위 호환성)
    person_contract_repo = contract_domain.get_person_contract_repo()

    # 3. Company 도메인
    from app.domains.company import init_repositories as init_company_repos
    from app.domains.company import init_services as init_company_services
    from app.domains import company as company_domain
    init_company_repos()
    init_company_services()

    # Company 도메인 전역 변수 할당 (하위 호환성)
    classification_repo = company_domain.get_classification_repo()
    organization_repo = company_domain.get_organization_repo()
    data_sharing_settings_repo = company_domain.get_data_sharing_settings_repo()

    # 4. User 도메인
    from app.domains.user import init_repositories as init_user_repos
    from app.domains.user import init_services as init_user_services
    from app.domains import user as user_domain
    init_user_repos()
    init_user_services()

    # User 도메인 전역 변수 할당 (하위 호환성)
    user_repo = user_domain.get_user_repo()
    notification_repo = user_domain.get_notification_repo()
    notification_preference_repo = user_domain.get_notification_preference_repo()
    personal_profile_repo = user_domain.get_personal_profile_repo()

    # 5. Platform 도메인
    from app.domains.platform import init_repositories as init_platform_repos
    from app.domains.platform import init_services as init_platform_services
    from app.domains import platform as platform_domain
    init_platform_repos()
    init_platform_services()

    # Platform 도메인 전역 변수 할당 (하위 호환성)
    system_setting_repo = platform_domain.get_system_setting_repo()
    audit_log_repo = platform_domain.get_audit_log_repo()

    # 6. Sync 도메인
    from app.domains.sync import init_repositories as init_sync_repos
    from app.domains.sync import init_services as init_sync_services
    from app.domains import sync as sync_domain
    init_sync_repos()
    init_sync_services()

    # Sync 도메인 전역 변수 할당 (하위 호환성)
    sync_log_repo = sync_domain.get_sync_log_repo()
