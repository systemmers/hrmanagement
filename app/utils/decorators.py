"""
인증 데코레이터 모듈

@login_required, @role_required 등 인증 관련 데코레이터를 제공합니다.
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort


def login_required(f):
    """
    로그인 필수 데코레이터

    사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            # 현재 URL을 next 파라미터로 전달
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """
    특정 역할 필수 데코레이터

    사용자가 지정된 역할 중 하나를 가지고 있어야 접근 가능합니다.

    사용 예:
        @role_required('admin')
        @role_required('admin', 'manager')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 먼저 로그인 확인
            if not session.get('user_id'):
                flash('로그인이 필요합니다.', 'error')
                return redirect(url_for('auth.login', next=request.url))

            # 역할 확인
            user_role = session.get('user_role')
            if user_role not in roles:
                flash('접근 권한이 없습니다.', 'error')
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    관리자 전용 데코레이터

    admin 역할을 가진 사용자만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))

        if session.get('user_role') != 'admin':
            flash('관리자만 접근 가능합니다.', 'error')
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def manager_or_admin_required(f):
    """
    매니저 또는 관리자 전용 데코레이터

    manager 또는 admin 역할을 가진 사용자만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))

        user_role = session.get('user_role')
        if user_role not in ('admin', 'manager'):
            flash('관리자 또는 매니저만 접근 가능합니다.', 'error')
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def self_or_admin_required(employee_id_param='employee_id'):
    """
    본인 또는 관리자 전용 데코레이터

    자신의 정보이거나 admin 역할인 경우에만 접근 가능합니다.

    사용 예:
        @self_or_admin_required('employee_id')
        def view_employee(employee_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash('로그인이 필요합니다.', 'error')
                return redirect(url_for('auth.login', next=request.url))

            # admin은 모든 접근 가능
            if session.get('user_role') == 'admin':
                return f(*args, **kwargs)

            # 본인 확인
            target_employee_id = kwargs.get(employee_id_param)
            if target_employee_id and session.get('employee_id') == int(target_employee_id):
                return f(*args, **kwargs)

            flash('접근 권한이 없습니다.', 'error')
            abort(403)

        return decorated_function
    return decorator
