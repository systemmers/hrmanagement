"""
Platform Dashboard

플랫폼 대시보드 라우트
"""
from flask import render_template

from . import platform_bp
from ...utils.decorators import superadmin_required
from ...models import User, Company
from ...models.person_contract import PersonCorporateContract


@platform_bp.route('/')
@superadmin_required
def dashboard():
    """플랫폼 대시보드"""
    # 통계 데이터
    stats = {
        'total_users': User.query.count(),
        'total_companies': Company.query.count(),
        'active_companies': Company.query.filter_by(is_active=True).count(),
        'total_contracts': PersonCorporateContract.query.count(),
        'active_contracts': PersonCorporateContract.query.filter_by(status='active').count(),
        'superadmins': User.query.filter_by(is_superadmin=True).count(),
    }

    # 최근 가입 사용자
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    # 최근 등록 법인
    recent_companies = Company.query.order_by(Company.created_at.desc()).limit(5).all()

    return render_template(
        'platform/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_companies=recent_companies
    )
