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


# ============================================================
# 계정 타입별 데코레이터
# ============================================================

def account_type_required(account_type: str, error_redirect: str = 'main.index'):
    """
    특정 계정 타입 필수 데코레이터

    Args:
        account_type: 'personal' 또는 'corporate'
        error_redirect: 권한 없을 때 리다이렉트할 URL

    사용 예:
        @account_type_required('personal')
        def personal_only_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                flash('로그인이 필요합니다.', 'error')
                return redirect(url_for('auth.login', next=request.url))

            if session.get('account_type') != account_type:
                type_name = '개인' if account_type == 'personal' else '법인'
                flash(f'{type_name} 계정으로 로그인해주세요.', 'error')
                return redirect(url_for(error_redirect))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def personal_login_required(f):
    """
    개인 계정 로그인 필수 데코레이터

    개인(personal) 계정으로 로그인한 경우에만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))

        if session.get('account_type') != 'personal':
            flash('개인 계정으로 로그인해주세요.', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


def corporate_login_required(f):
    """
    법인 계정 로그인 필수 데코레이터

    법인(corporate) 계정으로 로그인한 경우에만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))

        if session.get('account_type') != 'corporate':
            flash('법인 계정으로 로그인해주세요.', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


def corporate_admin_required(f):
    """
    법인 관리자 권한 필수 데코레이터

    법인 계정 중 admin 또는 manager 역할인 경우에만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.', 'error')
            return redirect(url_for('auth.login', next=request.url))

        if session.get('account_type') != 'corporate':
            flash('법인 계정으로 로그인해주세요.', 'error')
            return redirect(url_for('main.index'))

        if session.get('user_role') not in ('admin', 'manager'):
            flash('관리자 권한이 필요합니다.', 'error')
            return redirect(url_for('corporate.dashboard'))

        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# 계약 관련 데코레이터
# ============================================================

def personal_account_required(f):
    """
    개인 계정 필수 데코레이터 (API용)

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('account_type') != 'personal':
            flash('개인 계정으로만 접근할 수 있습니다.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def corporate_account_required(f):
    """
    법인 계정 필수 데코레이터 (API용)

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('account_type') != 'corporate':
            flash('법인 계정으로만 접근할 수 있습니다.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def contract_access_required(f):
    """
    계약 접근 권한 확인 데코레이터

    계약 당사자(개인 또는 법인)만 접근 가능합니다.
    contract_id를 URL 파라미터로 받는 함수에서 사용합니다.
    """
    @wraps(f)
    def decorated_function(contract_id, *args, **kwargs):
        from ..models.person_contract import PersonCorporateContract

        user_id = session.get('user_id')
        account_type = session.get('account_type')
        company_id = session.get('company_id')

        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            from flask import jsonify
            return jsonify({'success': False, 'error': '계약을 찾을 수 없습니다.'}), 404

        # 권한 확인
        is_person = contract.person_user_id == user_id
        is_company = account_type == 'corporate' and contract.company_id == company_id

        if not is_person and not is_company:
            from flask import jsonify
            return jsonify({'success': False, 'error': '접근 권한이 없습니다.'}), 403

        return f(contract_id, *args, **kwargs)
    return decorated_function


# ============================================================
# API 전용 데코레이터 (JSON 응답)
# ============================================================

def api_login_required(f):
    """
    API용 로그인 필수 데코레이터

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import jsonify
        if not session.get('user_id'):
            return jsonify({'success': False, 'error': '로그인이 필요합니다.'}), 401
        return f(*args, **kwargs)
    return decorated_function


def api_personal_account_required(f):
    """
    API용 개인 계정 필수 데코레이터

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import jsonify
        if session.get('account_type') != 'personal':
            return jsonify({'success': False, 'error': '개인 계정으로만 접근할 수 있습니다.'}), 403
        return f(*args, **kwargs)
    return decorated_function


def api_corporate_account_required(f):
    """
    API용 법인 계정 필수 데코레이터

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import jsonify
        if session.get('account_type') != 'corporate':
            return jsonify({'success': False, 'error': '법인 계정으로만 접근할 수 있습니다.'}), 403
        return f(*args, **kwargs)
    return decorated_function
