"""
Platform Dashboard

플랫폼 대시보드 라우트

Phase 7: 도메인 중심 마이그레이션 (app/domains/platform/blueprints/)
Phase 24: Model.query 제거 - PlatformService 경유
"""
from flask import render_template

from . import platform_bp
from app.shared.utils.decorators import superadmin_required
from app.domains.platform.services.platform_service import platform_service


@platform_bp.route('/')
@superadmin_required
def dashboard():
    """플랫폼 대시보드"""
    # 통계 데이터 (Service 경유)
    stats = platform_service.get_dashboard_stats()

    # 최근 가입 사용자 (Service 경유)
    recent_users = platform_service.get_recent_users(limit=5)

    # 최근 등록 법인 (Service 경유)
    recent_companies = platform_service.get_recent_companies(limit=5)

    return render_template(
        'domains/platform/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_companies=recent_companies
    )
