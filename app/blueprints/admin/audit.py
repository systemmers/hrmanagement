"""
감사 대시보드 라우트

Phase 5: 감사 로그 대시보드 UI
"""
from flask import render_template

from . import admin_bp
from ...shared.utils.decorators import login_required, admin_required


@admin_bp.route('/audit')
@login_required
@admin_required
def audit_dashboard():
    """감사 대시보드 페이지"""
    return render_template('admin/audit_dashboard.html')
