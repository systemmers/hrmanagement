"""
감사 대시보드 라우트

Phase 5: 감사 로그 대시보드 UI
"""
from flask import render_template, session
from functools import wraps

from . import admin_bp


def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """관리자 권한 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') not in ['admin', 'manager']:
            from flask import redirect, url_for, flash
            flash('관리자 권한이 필요합니다.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/audit')
@login_required
@admin_required
def audit_dashboard():
    """감사 대시보드 페이지"""
    return render_template('admin/audit_dashboard.html')
