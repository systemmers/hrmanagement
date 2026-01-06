"""
Blueprint 등록 모듈

모든 Blueprint를 앱에 등록합니다.
"""


def register_blueprints(app):
    """앱에 모든 Blueprint 등록

    Phase 7: 도메인 중심 마이그레이션 완료
    - 모든 Blueprint는 app/domains/에서 import
    - 레거시 경로 (app/blueprints/*.py)는 삭제됨
    """
    # 도메인 Blueprints
    from app.domains.employee.blueprints import employees_bp
    from app.domains.contract.blueprints import contracts_bp
    from app.domains.company.blueprints import corporate_bp
    from app.domains.company.blueprints.settings import corporate_settings_api_bp
    from app.domains.user.blueprints import auth_bp, mypage_bp, personal_bp, account_bp, notifications_bp
    from app.domains.platform.blueprints import platform_bp
    from app.domains.sync.blueprints import sync_bp

    # 미마이그레이션 Blueprints (app/blueprints/ 유지)
    from .main import main_bp
    from .api import api_bp
    from .ai_test import ai_test_bp
    from .admin import admin_bp
    from .audit import audit_bp
    from .profile import profile_bp

    # 플랫폼 관리자 (/platform/*) - 슈퍼관리자 전용
    app.register_blueprint(platform_bp)

    # 인증 관련 (/auth/*)
    app.register_blueprint(auth_bp)

    # 관리자 기능 (/admin/*)
    app.register_blueprint(admin_bp)

    # 법인 계정 (/corporate/*) - Phase 1
    app.register_blueprint(corporate_bp)

    # 개인 계정 (/personal/*) - Phase 2
    app.register_blueprint(personal_bp)

    # 계약 관리 (/contracts/*) - Phase 3
    app.register_blueprint(contracts_bp)

    # 데이터 동기화 (/api/sync/*) - Phase 4
    app.register_blueprint(sync_bp)

    # 감사 로그 (/api/audit/*) - Phase 4
    app.register_blueprint(audit_bp)

    # 알림 시스템 (/api/notifications/*) - Phase 5
    app.register_blueprint(notifications_bp)

    # 통합 프로필 (/profile/*) - 법인/개인 인터페이스 통합
    app.register_blueprint(profile_bp)

    # 계정 관리 (/account/*) - 설정, 비밀번호, 공개설정, 탈퇴
    app.register_blueprint(account_bp)

    # 마이페이지 - 일반 직원용 (/my/*)
    app.register_blueprint(mypage_bp)

    # 메인 페이지 (/, /search)
    app.register_blueprint(main_bp)

    # 직원 관리 CRUD (/employees/*)
    app.register_blueprint(employees_bp)

    # REST API (/api/*)
    app.register_blueprint(api_bp, url_prefix='/api')

    # AI 테스트 (프로토타입) (/ai-test/*)
    app.register_blueprint(ai_test_bp)

    # 법인 세팅 API (/api/corporate/*)
    app.register_blueprint(corporate_settings_api_bp)
