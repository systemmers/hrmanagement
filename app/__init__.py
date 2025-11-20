"""
Flask 애플리케이션 팩토리
앱 생성 및 확장 초기화
"""
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from config import config

# Flask 확장 초기화
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()


def create_app(config_name='default'):
    """Flask 애플리케이션 팩토리 함수"""

    app = Flask(__name__)

    # 설정 로드
    app.config.from_object(config[config_name])

    # locale selector 함수 정의
    def get_locale():
        """사용자의 언어 설정을 결정"""
        return request.accept_languages.best_match(['ko', 'en'])

    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    # Flask-Login 설정
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '로그인이 필요합니다.'
    login_manager.login_message_category = 'warning'

    # 유저 로더 콜백
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprint 등록
    from app.auth import auth_bp
    from app.employee import employee_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(employee_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')

    # 템플릿 필터
    @app.template_filter('first_char')
    def first_char(text):
        """안전하게 첫 글자 반환 (IndexError 방지)"""
        if text and len(text) > 0:
            return text[0]
        return '?'

    # 보안 헤더 추가
    @app.after_request
    def add_security_headers(response):
        """보안 헤더 추가"""
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https://i.pravatar.cc; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers['Content-Security-Policy'] = csp

        # 기타 보안 헤더
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        return response

    # 에러 핸들러
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': '페이지를 찾을 수 없습니다.'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': '서버 오류가 발생했습니다.'}, 500

    # CLI 커맨드
    @app.cli.command()
    def init_db():
        """데이터베이스 초기화"""
        db.create_all()
        print('데이터베이스가 초기화되었습니다.')

    return app
