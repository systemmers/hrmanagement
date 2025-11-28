"""
Flask 애플리케이션 설정 파일
"""
import os


class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 데이터 파일 경로 (app/ 패키지 기준)
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    EMPLOYEES_JSON = os.path.join(DATA_DIR, 'employees.json')
    CLASSIFICATION_OPTIONS_JSON = os.path.join(DATA_DIR, 'classification_options.json')

    # 확장 데이터 파일 경로
    EMPLOYEES_EXTENDED_JSON = os.path.join(DATA_DIR, 'employees_extended.json')
    EDUCATION_JSON = os.path.join(DATA_DIR, 'education.json')
    CAREERS_JSON = os.path.join(DATA_DIR, 'careers.json')
    CERTIFICATES_JSON = os.path.join(DATA_DIR, 'certificates.json')
    FAMILY_MEMBERS_JSON = os.path.join(DATA_DIR, 'family_members.json')
    LANGUAGES_JSON = os.path.join(DATA_DIR, 'languages.json')
    MILITARY_JSON = os.path.join(DATA_DIR, 'military.json')

    # Phase 2: 핵심 기능 데이터 파일 경로
    SALARIES_JSON = os.path.join(DATA_DIR, 'salaries.json')
    BENEFITS_JSON = os.path.join(DATA_DIR, 'benefits.json')
    CONTRACTS_JSON = os.path.join(DATA_DIR, 'contracts.json')
    SALARY_HISTORY_JSON = os.path.join(DATA_DIR, 'salary_history.json')

    # Phase 5: 급여 지급 이력 데이터 파일 경로
    SALARY_PAYMENTS_JSON = os.path.join(DATA_DIR, 'salary_payments.json')

    # Phase 3: 인사평가 기능 데이터 파일 경로
    PROMOTIONS_JSON = os.path.join(DATA_DIR, 'promotions.json')
    EVALUATIONS_JSON = os.path.join(DATA_DIR, 'evaluations.json')
    TRAININGS_JSON = os.path.join(DATA_DIR, 'trainings.json')
    ATTENDANCE_JSON = os.path.join(DATA_DIR, 'attendance.json')

    # Phase 4: 부가 기능 데이터 파일 경로
    INSURANCES_JSON = os.path.join(DATA_DIR, 'insurances.json')
    PROJECTS_JSON = os.path.join(DATA_DIR, 'projects.json')
    AWARDS_JSON = os.path.join(DATA_DIR, 'awards.json')
    ASSETS_JSON = os.path.join(DATA_DIR, 'assets.json')

    # Phase 6: 첨부파일 데이터 파일 경로
    ATTACHMENTS_JSON = os.path.join(DATA_DIR, 'attachments.json')

    # Flask 설정
    DEBUG = True
    TESTING = False

    # WTForms 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True


class ProductionConfig(Config):
    """운영 환경 설정"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    WTF_CSRF_ENABLED = False


# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
