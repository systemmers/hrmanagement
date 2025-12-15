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

    # AI 서비스 설정 (Gemini API)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Google Cloud 설정 (Vertex AI, Document AI, Vision OCR)
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    GOOGLE_PROJECT_ID = os.environ.get('GOOGLE_PROJECT_ID')
    GOOGLE_LOCATION = os.environ.get('GOOGLE_LOCATION', 'asia-northeast3')
    DOCUMENTAI_PROCESSOR_ID = os.environ.get('DOCUMENTAI_PROCESSOR_ID')
    DOCUMENTAI_LOCATION = os.environ.get('DOCUMENTAI_LOCATION', 'us')

    # Local LLM 설정 (LM Studio)
    LOCAL_LLM_ENDPOINT = os.environ.get('LOCAL_LLM_ENDPOINT', 'http://localhost:1234')
    LOCAL_LLM_MODEL = os.environ.get('LOCAL_LLM_MODEL', 'local-model')
    LOCAL_LLM_TIMEOUT = int(os.environ.get('LOCAL_LLM_TIMEOUT', '120'))

    # Vision OCR 설정
    VISION_OCR_ENABLED = os.environ.get('VISION_OCR_ENABLED', 'true').lower() == 'true'

    # SQLAlchemy 설정 (PostgreSQL 필수)
    # DATABASE_URL 환경변수 필수 - dotenv 로드 후 사용
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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

    # 세션 설정
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24시간

    # WTForms 설정
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # 통합 프로필 기능 플래그 (법인/개인 계정 인터페이스 통합)
    ENABLE_UNIFIED_PROFILE = os.environ.get('ENABLE_UNIFIED_PROFILE', 'true').lower() == 'true'
    UNIFIED_PROFILE_ROLLOUT_PERCENT = int(os.environ.get('UNIFIED_PROFILE_ROLLOUT_PERCENT', '100'))

    # 법인 관리자 프로필 기능 플래그
    ENABLE_CORPORATE_ADMIN_PROFILE = os.environ.get('ENABLE_CORPORATE_ADMIN_PROFILE', 'true').lower() == 'true'


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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'


# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
