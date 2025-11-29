"""
Blueprint 등록 모듈

모든 Blueprint를 앱에 등록합니다.
"""


def register_blueprints(app):
    """앱에 모든 Blueprint 등록"""
    from .main import main_bp
    from .employees import employees_bp
    from .classification import classification_bp
    from .api import api_bp
    from .ai_test import ai_test_bp
    from .auth import auth_bp
    from .admin import admin_bp
    from .mypage import mypage_bp

    # 인증 관련 (/auth/*)
    app.register_blueprint(auth_bp)

    # 관리자 기능 (/admin/*)
    app.register_blueprint(admin_bp)

    # 마이페이지 - 일반 직원용 (/my/*)
    app.register_blueprint(mypage_bp)

    # 메인 페이지 (/, /search)
    app.register_blueprint(main_bp)

    # 직원 관리 CRUD (/employees/*)
    app.register_blueprint(employees_bp)

    # 분류 옵션 관리 페이지 (/classification-options)
    app.register_blueprint(classification_bp)

    # REST API (/api/*)
    app.register_blueprint(api_bp, url_prefix='/api')

    # AI 테스트 (프로토타입) (/ai-test/*)
    app.register_blueprint(ai_test_bp)
