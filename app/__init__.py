"""
Flask 애플리케이션 팩토리
앱 생성 및 확장 초기화
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config

# Flask 확장 초기화
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """Flask 애플리케이션 팩토리 함수"""

    app = Flask(__name__)

    # 설정 로드
    app.config.from_object(config[config_name])

    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

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
