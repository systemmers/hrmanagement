"""
인증 데코레이터 모듈

@login_required, @role_required 등 인증 관련 데코레이터를 제공합니다.
Phase 6: 백엔드 리팩토링 - 중복 로직 통합
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, jsonify
from typing import Optional, Tuple, Callable


# ============================================================
# 헬퍼 함수 (중복 로직 통합)
# ============================================================

def _check_login() -> Optional[Tuple]:
    """
    로그인 상태 확인 (웹 페이지용)

    Returns:
        None: 로그인됨
        Tuple: (redirect_response,) 로그인 필요시 리다이렉트
    """
    if not session.get('user_id'):
        flash('로그인이 필요합니다.', 'error')
        return (redirect(url_for('auth.login', next=request.url)),)
    return None


def _check_api_login() -> Optional[Tuple]:
    """
    로그인 상태 확인 (API용)

    Returns:
        None: 로그인됨
        Tuple: (json_response, status_code) 로그인 필요시 JSON 응답
    """
    if not session.get('user_id'):
        return (jsonify({'success': False, 'error': '로그인이 필요합니다.'}), 401)
    return None


def _check_account_type(required_type: str, error_redirect: str = 'main.index') -> Optional[Tuple]:
    """
    계정 타입 확인 (웹 페이지용)

    Args:
        required_type: 'personal' 또는 'corporate'
        error_redirect: 권한 없을 때 리다이렉트할 URL

    Returns:
        None: 권한 있음
        Tuple: (redirect_response,) 권한 없을시 리다이렉트
    """
    if session.get('account_type') != required_type:
        type_name = '개인' if required_type == 'personal' else '법인'
        flash(f'{type_name} 계정으로 로그인해주세요.', 'error')
        return (redirect(url_for(error_redirect)),)
    return None


def _check_api_account_type(required_type: str) -> Optional[Tuple]:
    """
    계정 타입 확인 (API용)

    Args:
        required_type: 'personal' 또는 'corporate'

    Returns:
        None: 권한 있음
        Tuple: (json_response, status_code) 권한 없을시 JSON 응답
    """
    if session.get('account_type') != required_type:
        type_name = '개인' if required_type == 'personal' else '법인'
        return (jsonify({'success': False, 'error': f'{type_name} 계정으로만 접근할 수 있습니다.'}), 403)
    return None


def _check_role(*roles) -> Optional[Tuple]:
    """
    역할 확인

    Args:
        roles: 허용되는 역할들

    Returns:
        None: 권한 있음
        Tuple: (abort_response,) 권한 없을시 403
    """
    user_role = session.get('user_role')
    if user_role not in roles:
        flash('접근 권한이 없습니다.', 'error')
        return (abort(403),)
    return None


# ============================================================
# 기본 데코레이터
# ============================================================

def login_required(f):
    """
    로그인 필수 데코레이터

    사용자가 로그인하지 않은 경우 로그인 페이지로 리다이렉트합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        login_check = _check_login()
        if login_check:
            return login_check[0]
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
            login_check = _check_login()
            if login_check:
                return login_check[0]

            role_check = _check_role(*roles)
            if role_check:
                return role_check[0]

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
        login_check = _check_login()
        if login_check:
            return login_check[0]

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
        login_check = _check_login()
        if login_check:
            return login_check[0]

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
            login_check = _check_login()
            if login_check:
                return login_check[0]

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
            login_check = _check_login()
            if login_check:
                return login_check[0]

            type_check = _check_account_type(account_type, error_redirect)
            if type_check:
                return type_check[0]

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
        login_check = _check_login()
        if login_check:
            return login_check[0]

        type_check = _check_account_type('personal')
        if type_check:
            return type_check[0]

        return f(*args, **kwargs)
    return decorated_function


def corporate_login_required(f):
    """
    법인 계정 로그인 필수 데코레이터

    법인(corporate) 계정으로 로그인한 경우에만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        login_check = _check_login()
        if login_check:
            return login_check[0]

        type_check = _check_account_type('corporate')
        if type_check:
            return type_check[0]

        return f(*args, **kwargs)
    return decorated_function


def corporate_admin_required(f):
    """
    법인 관리자 권한 필수 데코레이터

    법인 계정 중 admin 또는 manager 역할인 경우에만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        login_check = _check_login()
        if login_check:
            return login_check[0]

        type_check = _check_account_type('corporate')
        if type_check:
            return type_check[0]

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
        api_check = _check_api_login()
        if api_check:
            return api_check
        return f(*args, **kwargs)
    return decorated_function


def api_personal_account_required(f):
    """
    API용 개인 계정 필수 데코레이터

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        type_check = _check_api_account_type('personal')
        if type_check:
            return type_check
        return f(*args, **kwargs)
    return decorated_function


def api_corporate_account_required(f):
    """
    API용 법인 계정 필수 데코레이터

    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        type_check = _check_api_account_type('corporate')
        if type_check:
            return type_check
        return f(*args, **kwargs)
    return decorated_function
