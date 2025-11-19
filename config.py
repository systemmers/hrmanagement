"""
Flask 애플리케이션 설정
환경별 설정 클래스 (개발, 프로덕션)
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """기본 설정"""

    # 보안 키
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # 데이터베이스
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 파일 업로드
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

    # 세션
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # 개발환경에서는 False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # WTForms
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """개발 환경 설정"""

    DEBUG = True
    TESTING = False

    # SQLite 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "insacard_dev.db")}'

    # 디버그 툴바
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class ProductionConfig(Config):
    """프로덕션 환경 설정"""

    DEBUG = False
    TESTING = False

    # PostgreSQL 데이터베이스 (환경변수에서 가져옴)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "insacard.db")}'

    # 보안 강화
    SESSION_COOKIE_SECURE = True  # HTTPS 필수

    # WTForms
    WTF_CSRF_TIME_LIMIT = 3600  # 1시간


class TestingConfig(Config):
    """테스트 환경 설정"""

    DEBUG = True
    TESTING = True

    # 테스트용 메모리 DB
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # CSRF 비활성화 (테스트용)
    WTF_CSRF_ENABLED = False


# 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
