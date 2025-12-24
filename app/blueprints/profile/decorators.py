"""
Profile Decorators - 통합 프로필 인증 데코레이터

법인 직원, 법인 관리자, 개인 계정에 대한 통합 인증 처리
Phase 8: 상수 모듈 적용
Phase 4.1: PersonalProfile → Profile 마이그레이션 완료
"""
from functools import wraps
from flask import session, g, flash, redirect, url_for, current_app

from app.constants.session_keys import SessionKeys, AccountType
from app.models.employee import Employee
from app.models.profile import Profile
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.adapters.profile_adapter import (
    EmployeeProfileAdapter,
    PersonalProfileAdapter,
    CorporateAdminProfileAdapter
)


def unified_profile_required(f):
    """
    통합 프로필 인증 데코레이터

    세션에서 account_type을 우선 확인하여 적절한 어댑터를 생성합니다.
    - 개인 계정: session['account_type'] == 'personal' -> PersonalProfileAdapter
      (개인 계정은 계약 승인 시 employee_id가 설정될 수 있지만 Profile 모델 사용)
    - 법인 직원: session['account_type'] == 'employee_sub' -> EmployeeProfileAdapter
    - 법인 관리자: session['account_type'] == 'corporate' -> CorporateAdminProfileAdapter

    생성된 어댑터는 g.profile에 저장됩니다.
    추가로 g.is_corporate (법인 소속 여부), g.is_admin (관리자 여부) 플래그가 설정됩니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get(SessionKeys.USER_ID)
        employee_id = session.get(SessionKeys.EMPLOYEE_ID)
        account_type = session.get(SessionKeys.ACCOUNT_TYPE)

        # 인증 확인
        if not user_id and not employee_id:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))

        # 기능 플래그 확인 (비활성화시 기존 라우트로 리다이렉트)
        if not current_app.config.get('ENABLE_UNIFIED_PROFILE', False):
            if employee_id or account_type == AccountType.CORPORATE:
                return redirect(url_for('mypage.company_info'))
            else:
                return redirect(url_for('personal.profile'))

        # 개인 계정 어댑터 생성 (account_type이 personal인 경우 - 우선 처리)
        # 개인 계정은 계약 승인 시 employee_id가 설정될 수 있지만,
        # 프로필 조회는 항상 Profile 모델(PersonalProfileAdapter)을 사용해야 함
        if account_type == AccountType.PERSONAL:
            # 통합 Profile 모델 조회
            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                # 프로필이 없으면 프로필 수정 페이지로 리다이렉트
                flash('프로필을 먼저 생성해주세요.', 'info')
                return redirect(url_for('personal.profile_edit'))

            g.profile = PersonalProfileAdapter(profile)
            g.is_corporate = False
            g.is_admin = False
            g.personal_profile = profile

        # 법인 직원 어댑터 생성 (employee_sub 계정)
        elif employee_id and account_type == AccountType.EMPLOYEE_SUB:
            employee = Employee.query.get(employee_id)
            if not employee:
                flash('직원 정보를 찾을 수 없습니다.', 'error')
                session.pop(SessionKeys.EMPLOYEE_ID, None)
                return redirect(url_for('auth.login'))

            g.profile = EmployeeProfileAdapter(employee)
            g.is_corporate = True
            g.is_admin = False
            g.employee = employee

        # 법인 관리자 계정 (account_type이 corporate인 경우)
        elif account_type == AccountType.CORPORATE:
            # 법인 관리자 프로필 기능 플래그 확인
            if not current_app.config.get('ENABLE_CORPORATE_ADMIN_PROFILE', False):
                flash('법인 관리자 프로필 기능이 비활성화되어 있습니다.', 'info')
                return redirect(url_for('main.index'))

            # 법인 관리자 프로필 조회
            admin_profile = CorporateAdminProfile.query.filter_by(user_id=user_id).first()
            if not admin_profile:
                # 프로필이 없으면 프로필 생성 안내
                flash('법인 관리자 프로필을 먼저 생성해주세요.', 'info')
                return redirect(url_for('profile.admin_profile_create'))

            g.profile = CorporateAdminProfileAdapter(admin_profile)
            g.is_corporate = True
            g.is_admin = True
            g.admin_profile = admin_profile

        # 그 외 (예외 케이스 - 정상적으로는 도달하지 않음)
        else:
            flash('계정 유형을 확인할 수 없습니다.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def corporate_only(f):
    """
    법인 직원 전용 데코레이터

    unified_profile_required로 인증 후 법인 직원만 접근 가능하도록 제한
    """
    @wraps(f)
    @unified_profile_required
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'is_corporate', False):
            flash('법인 직원만 접근 가능한 기능입니다.', 'warning')
            return redirect(url_for('profile.view'))
        return f(*args, **kwargs)
    return decorated_function


def corporate_admin_only(f):
    """
    법인 관리자 전용 데코레이터

    unified_profile_required로 인증 후 법인 관리자만 접근 가능하도록 제한
    """
    @wraps(f)
    @unified_profile_required
    def decorated_function(*args, **kwargs):
        if not getattr(g, 'is_admin', False):
            flash('법인 관리자만 접근 가능한 기능입니다.', 'warning')
            return redirect(url_for('profile.view'))
        return f(*args, **kwargs)
    return decorated_function
