"""
Profile Decorators - 통합 프로필 인증 데코레이터

법인 직원과 개인 계정에 대한 통합 인증 처리
"""
from functools import wraps
from flask import session, g, flash, redirect, url_for, current_app

from app.models.employee import Employee
from app.models.personal.profile import PersonalProfile
from app.adapters.profile_adapter import (
    EmployeeProfileAdapter,
    PersonalProfileAdapter
)


def unified_profile_required(f):
    """
    통합 프로필 인증 데코레이터

    세션에서 employee_id 또는 user_id를 확인하여 적절한 어댑터를 생성합니다.
    - 법인 직원: session['employee_id'] -> EmployeeProfileAdapter
    - 일반 개인: session['user_id'] -> PersonalProfileAdapter

    생성된 어댑터는 g.profile에 저장됩니다.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        employee_id = session.get('employee_id')
        account_type = session.get('account_type')

        # 인증 확인
        if not user_id and not employee_id:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('auth.login'))

        # 기능 플래그 확인 (비활성화시 기존 라우트로 리다이렉트)
        if not current_app.config.get('ENABLE_UNIFIED_PROFILE', False):
            if employee_id or account_type == 'corporate':
                return redirect(url_for('mypage.company_info'))
            else:
                return redirect(url_for('personal.profile'))

        # 법인 직원 어댑터 생성 (employee_id가 있는 경우)
        if employee_id:
            employee = Employee.query.get(employee_id)
            if not employee:
                flash('직원 정보를 찾을 수 없습니다.', 'error')
                session.pop('employee_id', None)
                return redirect(url_for('auth.login'))

            g.profile = EmployeeProfileAdapter(employee)
            g.is_corporate = True
            g.employee = employee

        # 법인 관리자 계정 (employee_id 없이 account_type이 corporate인 경우)
        elif account_type == 'corporate':
            # 법인 관리자는 개인 프로필이 없으므로 대시보드로 리다이렉트
            flash('법인 관리자 계정은 개인 프로필이 없습니다. 직원 목록에서 조회해주세요.', 'info')
            return redirect(url_for('main.index'))

        # 개인 계정 어댑터 생성
        else:
            profile = PersonalProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                # 프로필이 없으면 기존 프로필 페이지로 리다이렉트
                flash('프로필을 먼저 생성해주세요.', 'info')
                return redirect(url_for('personal.profile'))

            g.profile = PersonalProfileAdapter(profile)
            g.is_corporate = False
            g.personal_profile = profile

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
