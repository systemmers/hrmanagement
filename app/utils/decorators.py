"""
인증 데코레이터 모듈

@login_required, @role_required 등 인증 관련 데코레이터를 제공합니다.
Phase 6: 백엔드 리팩토링 - 중복 로직 통합
Phase 8: 매직 스트링 상수화 적용
"""
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort, jsonify
from typing import Optional, Tuple, Callable

from app.constants import SessionKeys, AccountType, UserRole, FlashMessages, ErrorMessages


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
    if not session.get(SessionKeys.USER_ID):
        flash(FlashMessages.LOGIN_REQUIRED, 'error')
        return (redirect(url_for('auth.login', next=request.url)),)
    return None


def _check_api_login() -> Optional[Tuple]:
    """
    로그인 상태 확인 (API용)

    Returns:
        None: 로그인됨
        Tuple: (json_response, status_code) 로그인 필요시 JSON 응답
    """
    if not session.get(SessionKeys.USER_ID):
        return (jsonify({'success': False, 'error': ErrorMessages.LOGIN_REQUIRED}), 401)
    return None


def _check_account_type(required_type: str, error_redirect: str = 'main.index') -> Optional[Tuple]:
    """
    계정 타입 확인 (웹 페이지용)

    Args:
        required_type: AccountType.PERSONAL 또는 AccountType.CORPORATE
        error_redirect: 권한 없을 때 리다이렉트할 URL

    Returns:
        None: 권한 있음
        Tuple: (redirect_response,) 권한 없을시 리다이렉트
    """
    if session.get(SessionKeys.ACCOUNT_TYPE) != required_type:
        if required_type == AccountType.PERSONAL:
            flash(FlashMessages.PERSONAL_ACCOUNT_REQUIRED, 'error')
        else:
            flash(FlashMessages.CORPORATE_ACCOUNT_REQUIRED, 'error')
        return (redirect(url_for(error_redirect)),)
    return None


def _check_api_account_type(required_type: str) -> Optional[Tuple]:
    """
    계정 타입 확인 (API용)

    Args:
        required_type: AccountType.PERSONAL 또는 AccountType.CORPORATE

    Returns:
        None: 권한 있음
        Tuple: (json_response, status_code) 권한 없을시 JSON 응답
    """
    if session.get(SessionKeys.ACCOUNT_TYPE) != required_type:
        if required_type == AccountType.PERSONAL:
            return (jsonify({'success': False, 'error': ErrorMessages.PERSONAL_ONLY}), 403)
        else:
            return (jsonify({'success': False, 'error': ErrorMessages.CORPORATE_ONLY}), 403)
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
    user_role = session.get(SessionKeys.USER_ROLE)
    if user_role not in roles:
        flash(FlashMessages.ACCESS_DENIED, 'error')
        return (abort(403),)
    return None


def _check_superadmin() -> Optional[Tuple]:
    """
    슈퍼관리자 여부 확인 (웹 페이지용)

    Returns:
        None: 슈퍼관리자
        Tuple: (abort_response,) 권한 없을시 403
    """
    if not session.get(SessionKeys.IS_SUPERADMIN):
        flash(FlashMessages.SUPERADMIN_REQUIRED, 'error')
        return (abort(403),)
    return None


def _check_api_superadmin() -> Optional[Tuple]:
    """
    슈퍼관리자 여부 확인 (API용)

    Returns:
        None: 슈퍼관리자
        Tuple: (json_response, status_code) 권한 없을시 JSON 응답
    """
    if not session.get(SessionKeys.IS_SUPERADMIN):
        return (jsonify({'success': False, 'error': ErrorMessages.SUPERADMIN_REQUIRED}), 403)
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

        if session.get(SessionKeys.USER_ROLE) != UserRole.ADMIN:
            flash(FlashMessages.ADMIN_REQUIRED, 'error')
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

        user_role = session.get(SessionKeys.USER_ROLE)
        if user_role not in UserRole.admin_roles():
            flash(FlashMessages.ADMIN_OR_MANAGER_REQUIRED, 'error')
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
            if session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN:
                return f(*args, **kwargs)

            # 본인 확인
            target_employee_id = kwargs.get(employee_id_param)
            if target_employee_id and session.get(SessionKeys.EMPLOYEE_ID) == int(target_employee_id):
                return f(*args, **kwargs)

            flash(FlashMessages.ACCESS_DENIED, 'error')
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
        account_type: AccountType.PERSONAL 또는 AccountType.CORPORATE
        error_redirect: 권한 없을 때 리다이렉트할 URL

    사용 예:
        @account_type_required(AccountType.PERSONAL)
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

        type_check = _check_account_type(AccountType.PERSONAL)
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

        type_check = _check_account_type(AccountType.CORPORATE)
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

        type_check = _check_account_type(AccountType.CORPORATE)
        if type_check:
            return type_check[0]

        if session.get(SessionKeys.USER_ROLE) not in UserRole.admin_roles():
            flash(FlashMessages.ADMIN_PERMISSION_REQUIRED, 'error')
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
        if session.get(SessionKeys.ACCOUNT_TYPE) != AccountType.PERSONAL:
            flash(FlashMessages.PERSONAL_ONLY_ACCESS, 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def personal_or_employee_account_required(f):
    """
    개인 또는 직원 계정 필수 데코레이터 (21번 원칙)

    개인(personal) 또는 직원(employee_sub) 계정으로 로그인한 경우에만 접근 가능합니다.
    계약 승인/거절 등 개인-법인 계약 관련 기능에서 사용합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        account_type = session.get(SessionKeys.ACCOUNT_TYPE)
        if account_type not in AccountType.personal_types():
            flash(FlashMessages.PERSONAL_OR_EMPLOYEE_ONLY, 'warning')
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
        if session.get(SessionKeys.ACCOUNT_TYPE) != AccountType.CORPORATE:
            flash(FlashMessages.CORPORATE_ONLY_ACCESS, 'warning')
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

        user_id = session.get(SessionKeys.USER_ID)
        account_type = session.get(SessionKeys.ACCOUNT_TYPE)
        company_id = session.get(SessionKeys.COMPANY_ID)

        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return jsonify({'success': False, 'error': ErrorMessages.CONTRACT_NOT_FOUND}), 404

        # 권한 확인
        is_person = contract.person_user_id == user_id
        is_company = account_type == AccountType.CORPORATE and contract.company_id == company_id

        if not is_person and not is_company:
            return jsonify({'success': False, 'error': ErrorMessages.ACCESS_DENIED}), 403

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
        type_check = _check_api_account_type(AccountType.PERSONAL)
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
        type_check = _check_api_account_type(AccountType.CORPORATE)
        if type_check:
            return type_check
        return f(*args, **kwargs)
    return decorated_function


def api_admin_or_manager_required(f):
    """
    API용 관리자/매니저 권한 필수 데코레이터

    admin 또는 manager 역할을 가진 사용자만 접근 가능합니다.
    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get(SessionKeys.USER_ROLE) not in UserRole.admin_roles():
            return jsonify({'success': False, 'error': ErrorMessages.ADMIN_PERMISSION_REQUIRED}), 403
        return f(*args, **kwargs)
    return decorated_function


def company_id_required(f):
    """
    법인 ID 필수 데코레이터

    세션에서 company_id를 검증하고 함수에 주입합니다.
    corporate_settings_api 등에서 반복되는 company_id 검증 로직을 추출한 데코레이터입니다.

    사용 예:
        @corporate_admin_required
        @company_id_required
        def get_settings(company_id):
            # company_id가 자동으로 주입됨
            return corporate_settings_service.get_settings(company_id)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        company_id = session.get(SessionKeys.COMPANY_ID)
        if not company_id:
            return jsonify({'success': False, 'error': '법인 정보를 찾을 수 없습니다.'}), 403
        return f(*args, company_id=company_id, **kwargs)
    return decorated_function


# ============================================================
# 플랫폼 관리자 데코레이터
# ============================================================

def superadmin_required(f):
    """
    플랫폼 마스터 관리자 전용 데코레이터

    is_superadmin=True인 사용자만 접근 가능합니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        login_check = _check_login()
        if login_check:
            return login_check[0]

        superadmin_check = _check_superadmin()
        if superadmin_check:
            return superadmin_check[0]

        return f(*args, **kwargs)
    return decorated_function


def api_superadmin_required(f):
    """
    API용 플랫폼 마스터 관리자 전용 데코레이터

    is_superadmin=True인 사용자만 접근 가능합니다.
    JSON 응답을 반환하는 API 엔드포인트용입니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_check = _check_api_login()
        if api_check:
            return api_check

        superadmin_check = _check_api_superadmin()
        if superadmin_check:
            return superadmin_check

        return f(*args, **kwargs)
    return decorated_function
