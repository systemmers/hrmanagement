"""
인사카드 관리 시스템 Flask 애플리케이션

App Factory 패턴을 사용하여 애플리케이션을 생성합니다.
"""
import os
from flask import Flask, render_template


def create_app(config_name=None):
    """앱 팩토리 함수"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # 설정 로드
    from .config import config
    app.config.from_object(config[config_name])

    # DATABASE_URL 필수 검증
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise ValueError("DATABASE_URL environment variable is required")

    # 데이터베이스 초기화
    from .database import db
    db.init_app(app)

    # SQLAlchemy 모델 import (테이블 생성 전 필수)
    from .models import (
        Employee, Education, Career, Certificate, FamilyMember,
        Language, MilitaryService, Salary, Benefit, Contract,
        SalaryHistory, Promotion, Evaluation, Training, Attendance,
        Insurance, HrProject, ProjectParticipation, Award, Asset, SalaryPayment, Attachment,
        ClassificationOption
    )

    # 테이블 생성 (개발 환경)
    with app.app_context():
        db.create_all()

    # 확장 초기화
    from .extensions import init_extensions
    init_extensions(app)

    # Blueprint 등록
    from .blueprints import register_blueprints
    register_blueprints(app)

    # 템플릿 유틸리티
    from .shared.utils.template_helpers import register_template_utils
    register_template_utils(app)

    # 인증 컨텍스트 프로세서
    from .shared.utils.context_processors import register_context_processors
    register_context_processors(app)

    # 에러 핸들러
    register_error_handlers(app)

    # CLI 명령어 등록
    from .cli import register_cli_commands
    register_cli_commands(app)

    return app


def register_error_handlers(app):
    """에러 핸들러 등록"""

    @app.errorhandler(403)
    def forbidden_error(error):
        """403 에러 핸들러"""
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """404 에러 핸들러"""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 핸들러"""
        return render_template('errors/500.html'), 500
