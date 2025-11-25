"""
Flask 애플리케이션 설정 파일
"""
import os

class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 데이터 파일 경로
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
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

